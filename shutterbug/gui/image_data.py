from astropy import stats

from photutils.detection import DAOStarFinder
from photutils.aperture import CircularAperture, CircularAnnulus, aperture_photometry

from pydantic import BaseModel

import numpy as np

from pathlib import Path

import logging

from typing import List


class SelectedStar(BaseModel):
    """Only for stars the user as explicitly selected"""

    index: int
    x: float
    y: float
    fwhm: float | None = None
    flux: float | None = None
    magnitude: float | None = None
    mag_error: float | None = None
    is_target: bool = False
    is_reference: bool = False


class FITSImage:
    def __init__(self, filepath: str, data) -> None:
        # File data
        self.filepath: Path = Path(filepath)
        self.filename: str = self.filepath.name
        self.observation_time: float
        self.original_data = data

        # Image display settings
        self.brightness_offset: int = 0
        self.contrast_factor: float = 1.0

        # Star variables, computed
        self.background: float | None = None
        self.stars = None  # Detected stars
        self.target_star_idx: int | None = None  # Index into the stars table
        self.reference_star_idxs: List[int] = []
        self._background_subtracted = None

    def compute_background(self):
        """Calculate background of image using sigma-clipped statistics"""

        _, median, _ = stats.sigma_clipped_stats(self.original_data, sigma=3.0)
        self.background = median
        return self.background

    def get_background_subtracted(self):
        """Get background-subtracted data, creates if unavailable"""
        if self._background_subtracted is None:
            if self.background is None:
                self.compute_background()
            # Simply subtract background from original data
            self._background_subtracted = self.original_data - self.background
        return self._background_subtracted

    def find_stars(self):
        """Detect stars using DAOStarFinder"""

        bg_subtracted = self.get_background_subtracted()

        # Estimate FWHM and threshold
        _, _, std = stats.sigma_clipped_stats(bg_subtracted, sigma=3.0)

        daofind = DAOStarFinder(fwhm=3.0, threshold=5.0 * std)
        self.stars = daofind(bg_subtracted)

        return self.stars

    def find_nearest_star(self, x: float, y: float, max_distance: int = 20):
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
        data = data * self.contrast_factor

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
        aperture_radius: int = 10,
        annulus_inner: int = 15,
        annulus_outer: int = 20,
    ):
        """Measure the instrumental magnitude of a star"""
        if self.target_star_idx is None:
            return

        star = self.get_star(self.target_star_idx)
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
        magnitude = -2.5 * np.log10(star_flux.value[0]) + 25

        return {
            "flux": star_flux.value[0],
            "magnitude": magnitude,
            "background": bkg_mean.value[0],
        }

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