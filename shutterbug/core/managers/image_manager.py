from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from shutterbug.core.app_controller import AppController

import logging
from typing import Dict, List

import numpy as np
from astropy import stats
from photutils.detection import DAOStarFinder
from PySide6.QtCore import QPoint, Signal
from shutterbug.core.models import FITSModel

from .base_manager import BaseManager


class ImageManager(BaseManager):
    """Manages multiple images and tracks which is active"""

    image_added = Signal(FITSModel)
    active_image_changed = Signal(FITSModel)
    image_removed = Signal(FITSModel)

    # Star Finding defaults
    MAX_DISTANCE_DEFAULT = 20  # pixels
    SIGMA_DEFAULT = 3.0
    FWHM_DEFAULT = 3.0
    THRESHOLD_DEFAULT = 5.0

    def __init__(self, controller: AppController, parent=None):

        super().__init__(controller, parent)
        self.images: Dict[str, FITSModel] = {}
        self.active_image: FITSModel | None = None

        # photometry settings
        self.fwhm: float = self.FWHM_DEFAULT
        self.threshold: float = self.THRESHOLD_DEFAULT
        self.sigma: float = self.SIGMA_DEFAULT

        logging.debug("Initialized Image Manager")

    def add_image(self, image: FITSModel):
        """Add image to manager"""
        self.images[image.filename] = image
        self.compute_stats(image)
        self.build_base_preview(image)
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

    def find_nearest_centroid(
        self,
        image: FITSModel,
        x: float,
        y: float,
        max_distance: int = MAX_DISTANCE_DEFAULT,
    ):
        stamp = image.get_stamp(x, y, max_distance)
        centroids = self.find_centroids(stamp)

        if centroids is None:
            return

        # Get stamp center
        stamp_size = stamp.shape[0]
        s_x, s_y = stamp_size / 2, stamp_size / 2
        # Calculate distance to all stars
        distances = np.sqrt(
            (centroids["xcentroid"] - s_x) ** 2 + (centroids["ycentroid"] - s_y) ** 2
        )

        min_idx = np.argmin(distances)

        if distances[min_idx] <= max_distance:
            centroid = centroids[min_idx]
            # Recalculate on image coordinates
            centroid["xcentroid"] = x + centroid["xcentroid"] - s_x
            centroid["ycentroid"] = y + centroid["ycentroid"] - s_y
            return centroids[min_idx]

        return None

    def _compute_background(self, data):
        """Calculate background of image using sigma-clipped statistics"""

        _, median, _ = stats.sigma_clipped_stats(data, sigma=self.sigma)

        return median

    def get_background_subtracted(self, data):
        """Get background-subtracted data, creates if unavailable"""
        background = self._compute_background(data)
        background_subtracted = data - background
        return background_subtracted

    def find_centroids_from_points(self, start: QPoint, end: QPoint, threshold: float):
        if self.active_image is None:
            return []
        x0, x1 = start.x(), end.x()
        y0, y1 = start.y(), end.y()

        # Account for every possible drag direction
        if y1 < y0:
            y1, y0 = y0, y1
        if x1 < x0:
            x1, x0 = x0, x1

        data = self.active_image.get_stamp_from_points(x0, x1, y0, y1)
        # Prevent error from having no area to search
        h = data.shape[0]
        w = data.shape[1]
        if (h * w) <= 50:
            return  # Not enough area

        centroids = self.find_centroids(data, threshold)
        if centroids is None:
            return []

        # Recalculate on image coordinates
        centroids["xcentroid"] = x0 + centroids["xcentroid"]
        centroids["ycentroid"] = y0 + centroids["ycentroid"]

        return centroids

    def find_centroids(self, data, threshold: float = THRESHOLD_DEFAULT):
        """Detect centroids using DAOStarFinder"""
        bg_subtracted = self.get_background_subtracted(data)
        if bg_subtracted is None:
            return

        # Estimate FWHM and threshold
        _, _, std = stats.sigma_clipped_stats(bg_subtracted, sigma=self.sigma)

        daofind = DAOStarFinder(fwhm=self.fwhm, threshold=threshold * std)
        centroids = daofind(bg_subtracted)

        return centroids

    def compute_stats(self, image: FITSModel):
        """Computes the statistics of the image for display"""
        data = image.data

        image.data_min = float(np.min(data))
        image.data_max = float(np.max(data))

        # Percentiles
        image.p_min, image.p_max = np.percentile(data, (0.5, 99.5))

        # Histogram

        image.histogram, image.bin_edges = np.histogram(
            data,
            bins=2048,
            range=(image.data_min, image.data_max),
        )

    def build_base_preview(self, image: FITSModel):
        """Builds preview data of the image"""
        scaled = (image.data - image.p_min) / (image.p_max - image.p_min)
        scaled = np.clip(scaled, 0, 1)
        image.display_data = (scaled * 255).astype(np.uint8)
