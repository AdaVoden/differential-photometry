import logging
from typing import Dict, List

import numpy as np
from astropy import stats
from photutils.detection import DAOStarFinder
from PySide6.QtCore import QObject, Signal
from shutterbug.core.models import FITSModel


class ImageManager(QObject):
    """Manages multiple images and tracks which is active"""

    _instance = None

    image_added = Signal(FITSModel)
    active_image_changed = Signal(FITSModel)
    image_removed = Signal(FITSModel)

    # Star Finding defaults
    MAX_DISTANCE_DEFAULT = 20  # pixels
    SIGMA_DEFAULT = 3.0
    FWHM_DEFAULT = 3.0
    THRESHOLD_DEFAULT = 5.0

    def __init__(self):
        if not hasattr(self, "_initialized"):
            self._initialized = True

            super().__init__()
            self.images: Dict[str, FITSModel] = {}
            self.active_image: FITSModel | None = None

            # photometry settings
            self.fwhm: float = self.FWHM_DEFAULT
            self.threshold: float = self.THRESHOLD_DEFAULT
            self.sigma: float = self.SIGMA_DEFAULT

    def __new__(cls):
        if cls._instance is None:
            logging.debug("Creating Image Manager singleton")
            cls._instance = super().__new__(cls)

        return cls._instance

    def add_image(self, image: FITSModel):
        """Add image to manager"""
        self.images[image.filename] = image
        self.image_added.emit(image)

    def set_active_image(self, image: FITSModel | None):
        """Sets active image"""
        if self.active_image != image:
            if image is None:
                logging.debug(f"Setting active image to None")
            else:
                logging.debug(f"Setting image as active: {image.filename}")
            self.active_image = image
            self.active_image_changed.emit(image)

    def remove_image(self, image: FITSModel):
        """Removes image from manager"""
        if image.filename in self.images.keys():
            self.images.pop(image.filename)

        if self.active_image == image:
            self.active_image = None
            self.active_image_changed.emit(self.active_image)
        self.image_removed.emit(image)

    def get_image(self, image_name: str) -> FITSModel | None:
        """Returns image from manager"""
        if image_name in self.images.keys():
            return self.images[image_name]
        return None

    def get_all_images(self) -> List[FITSModel]:
        """Returns the master list of images from manager"""
        return list(self.images.values())

    def find_nearest_star(
        self, x: float, y: float, max_distance: int = MAX_DISTANCE_DEFAULT
    ):
        image = self.active_image
        if image is None:
            return None  # No work to do!

        if image.stars is None:
            self.find_stars()

        if image.stars is None:
            # No stars found
            return None

        stars = image.stars

        # Calculate distance to all stars
        distances = np.sqrt(
            (stars["xcentroid"] - x) ** 2 + (stars["ycentroid"] - y) ** 2
        )

        min_idx = np.argmin(distances)

        if distances[min_idx] <= max_distance:
            return stars[min_idx]

        return None

    def _compute_background(self):
        """Calculate background of image using sigma-clipped statistics"""
        if self.active_image is None:
            return  # No work to do

        image = self.active_image
        _, median, _ = stats.sigma_clipped_stats(image.data, sigma=self.sigma)
        image.background = median
        return median

    def get_background_subtracted(self):
        """Get background-subtracted data, creates if unavailable"""
        if self.active_image is None:
            return  # No work to do

        image = self.active_image

        if image.background is None:
            self._compute_background()
            # Simply subtract background from original data
        background_subtracted = image.data - image.background
        return background_subtracted

    def find_stars(self):
        """Detect stars using DAOStarFinder"""
        image = self.active_image
        if image is None:
            return

        bg_subtracted = self.get_background_subtracted()
        if bg_subtracted is None:
            return

        # Estimate FWHM and threshold
        _, _, std = stats.sigma_clipped_stats(bg_subtracted, sigma=self.sigma)

        daofind = DAOStarFinder(fwhm=self.fwhm, threshold=self.threshold * std)
        image.stars = daofind(bg_subtracted)

        return image.stars

    def get_8bit_preview(self):
        """Gets the 8bit display version of the image data"""
        if self.active_image is None:
            return None

        if self.active_image.display_data is not None:
            return self.active_image.display_data

        self.active_image.display_data = self._compute_8bit_preview(self.active_image)
        return self.active_image.display_data

    def _compute_8bit_preview(self, image: FITSModel):
        """Computes the 8 bit display image from image data"""

        bzero = image.bzero
        bscale = image.bscale
        # Get and scale data appropriately
        data = bzero + (image.data * bscale)

        # Handle NaNs and Infs
        data = np.nan_to_num(data, nan=0.0, posinf=0.0, neginf=0.0)

        # Simple fixed percentiel stretch
        vmin, vmax = np.percentile(data, [1, 99])

        # clip and normalize to 0-1
        data = np.clip(data, vmin, vmax)
        data = (data - vmin) / (vmax - vmin)

        # clip and convert to 0-255
        data = np.clip(data, 0, 1)
        data = (data * 255).astype(np.uint8)

        return data
