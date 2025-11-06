from astropy import stats

from photutils.detection import DAOStarFinder
from photutils.aperture import CircularAperture, CircularAnnulus, aperture_photometry

from PySide6.QtCore import Signal, QObject

from pydantic import BaseModel

import numpy as np

from pathlib import Path

import logging

from typing import List

from shutterbug.gui.stars import StarManager


class FITSImage(QObject):
    """FITS image data and display class"""

    brightness_changed = Signal(int)
    contrast_changed = Signal(int)

    # Photometry defaults
    APERTURE_RADIUS_DEFAULT = 10  # pixels
    ANNULUS_INNER_DEFAULT = 15  # pixels
    ANNULUS_OUTER_DEFAULT = 20  # pixels
    ZERO_POINT_DEFAULT = 25

    # Star Finding defaults
    MAX_DISTANCE_DEFAULT = 20  # pixels
    SIGMA_DEFAULT = 3.0
    FWHM_DEFAULT = 3.0
    THRESHOLD_DEFAULT = 5.0

    # Display defaults
    BRIGHTNESS_OFFSET = 0
    CONTRAST_FACTOR = 100

    def __init__(self, filepath: Path, data, obs_time: str) -> None:
        super().__init__()
        # File data
        self.filepath: Path = filepath
        self.filename: str = self.filepath.name
        self.observation_time: float = float(obs_time)
        self.original_data = data

        # Star manager
        self.star_manager = StarManager()

        # Image display settings
        self.brightness_offset: int = self.BRIGHTNESS_OFFSET
        self.contrast_factor: int = self.CONTRAST_FACTOR

        # photometry settings
        self.zero_point: float = self.ZERO_POINT_DEFAULT
        self.fwhm: float = self.FWHM_DEFAULT
        self.threshold: float = self.THRESHOLD_DEFAULT
        self.sigma: float = self.SIGMA_DEFAULT

        # Star variables, computed
        self.background: float | None = None
        self.stars = None  # Detected stars
        self.target_star_idx: int | None = None  # Index into the stars table
        self.reference_star_idxs: List[int] = []

    def compute_background(self):
        """Calculate background of image using sigma-clipped statistics"""

        _, median, _ = stats.sigma_clipped_stats(
            self.original_data, sigma=self.SIGMA_DEFAULT
        )
        self.background = median
        return self.background

    def get_background_subtracted(self):
        """Get background-subtracted data, creates if unavailable"""
        if self.background is None:
            self.compute_background()
            # Simply subtract background from original data
        background_subtracted = self.original_data - self.background
        return background_subtracted

    def find_stars(self):
        """Detect stars using DAOStarFinder"""

        bg_subtracted = self.get_background_subtracted()

        # Estimate FWHM and threshold
        _, _, std = stats.sigma_clipped_stats(bg_subtracted, sigma=self.sigma)

        daofind = DAOStarFinder(fwhm=self.fwhm, threshold=self.threshold * std)
        self.stars = daofind(bg_subtracted)

        return self.stars

    def find_nearest_star(
        self, x: float, y: float, max_distance: int = MAX_DISTANCE_DEFAULT
    ):
        if self.stars is None:
            self.find_stars()

        if self.stars is None:
            # No stars found
            return None, None

        stars = self.stars

        # Calculate distance to all stars
        distances = np.sqrt(
            (stars["xcentroid"] - x) ** 2 + (stars["ycentroid"] - y) ** 2
        )

        min_idx = np.argmin(distances)

        if distances[min_idx] <= max_distance:
            return stars[min_idx], min_idx

        return None, None

    def get_normalized_data(self):
        """Normalize the FITS data to 0-255 for display"""

        # Handle NaNs and Infs
        data = np.nan_to_num(self.original_data, nan=0.0, posinf=0.0, neginf=0.0)

        # Simple fixed percentile stretch
        vmin, vmax = np.percentile(data, [1, 99])

        # Clip and normalize to 0-1 first
        data = np.clip(data, vmin, vmax)
        data = (data - vmin) / (vmax - vmin + 1e-10)  # Avoid divide by zero

        # apply contrast and brightness to 0-1 range
        # Contrast: multiply (1.0 = no change)
        data = data * (self.contrast_factor / 100)  # Normalize to ~1

        # Brightness: add/subtract (-1 to 1 range)
        data = data + (self.brightness_offset / 100.0)

        # Clip to 0-1 and convert to 0-255
        data = np.clip(data, 0, 1)
        data = (data * 255).astype(np.uint8)

        return data

    def get_star(self, idx):
        if self.stars is None:
            return None
        star = self.stars[idx]

        return SelectedStar(
            index=idx,
            x=star["xcentroid"],
            y=star["ycentroid"],
            flux=star["flux"],
            magnitude=None,
        )

    def measure_star_magnitude(
        self,
        aperture_radius: int = APERTURE_RADIUS_DEFAULT,
        annulus_inner: int = ANNULUS_INNER_DEFAULT,
        annulus_outer: int = ANNULUS_OUTER_DEFAULT,
    ):
        """Measure the instrumental magnitude of a star"""
        if self.target_star_idx is None:
            return

        return self.measure_magnitude_at_idx(
            self.target_star_idx, aperture_radius, annulus_inner, annulus_outer
        )

    def measure_magnitude_at_idx(
        self,
        idx: int,
        aperture_radius: int = APERTURE_RADIUS_DEFAULT,
        annulus_inner: int = ANNULUS_INNER_DEFAULT,
        annulus_outer: int = ANNULUS_OUTER_DEFAULT,
    ):
        star = self.get_star(idx)
        if star is None:
            return

        # Define apertures
        position = [(star.x, star.y)]
        aperture = CircularAperture(position, r=aperture_radius)
        annulus = CircularAnnulus(position, r_in=annulus_inner, r_out=annulus_outer)

        # Measure flux
        data = self.original_data
        phot_table = aperture_photometry(data, [aperture, annulus])

        # Background subtraction
        bkg_mean = phot_table["aperture_sum_1"] / annulus.area
        total_bkg = bkg_mean * aperture.area
        star_flux = phot_table["aperture_sum_0"] - total_bkg

        # Convert to magnitude (25 is an arbitrary zero_point)
        magnitude = -2.5 * np.log10(star_flux.value[0]) + self.zero_point

        star.magnitude = magnitude
        star.flux = star_flux.value[0]

        return star

    def select_star_at_position(self, x: float, y: float):
        """From specified coordinates, find star nearest to click"""

        if self.stars is None:
            return None, None

        nearest_star, idx = self.find_nearest_star(x, y)

        if nearest_star and idx:
            star_x = nearest_star["xcentroid"]
            star_y = nearest_star["ycentroid"]
            logging.info(f"Selected star at ({star_x:.1f}, {star_y:.1f})")
            return self.get_star(idx), idx

        else:
            logging.info(f"No star found near ({x:.1f}, {y:.1f})")
            return None, None

    @property
    def brightness(self):
        """Gets image's display brightness"""
        return self.brightness_offset

    @brightness.setter
    def brightness(self, value: int):
        """Sets image's display brightness"""
        if self.brightness_offset != value:
            self.brightness_offset = value
            self.brightness_changed.emit(value)

    @property
    def contrast(self):
        """Gets image's display contrast"""
        return self.contrast_factor

    @contrast.setter
    def contrast(self, value: int):
        """Sets image's display contrast"""
        if self.contrast_factor != value:
            self.contrast_factor = value
            self.contrast_changed.emit(value)
