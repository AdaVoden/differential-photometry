from astropy import stats
from photutils.detection import DAOStarFinder

from photutils.aperture import CircularAperture, CircularAnnulus, aperture_photometry

from pydantic import BaseModel

import numpy as np

from pathlib import Path

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
        self.filepath: Path = Path(filepath)
        self.filename: str = self.filepath.name + self.filepath.suffix
        self.original_data = data
        self.brightness_offset: int = 0
        self.contrast_factor: float = 1.0
        self.background: float | None = None
        self.stars = None  # Detected stars
        self.selected_star = None # Index into the stars table
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
    
    def select_star(self, idx, flux):
        if self.stars is None:
            return
        star = self.stars[idx]

        self.selected_star = SelectedStar(
            index = idx,
            x = star['xcentroid'],
            y = star['ycentroid'],
            flux = flux,
            magnitude = None
        )

    def measure_star_magnitude(
        self,
        aperture_radius: int = 10,
        annulus_inner: int = 15,
        annulus_outer: int = 20,
    ):
        """Measure the instrumental magnitude of a star"""
        if self.selected_star is None:
            return

        star_x = self.selected_star.x
        star_y = self.selected_star.y

        # Define apertures
        position = [(star_x, star_y)]
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

        self.selected_star.magnitude = magnitude
        
        return {
            "flux": star_flux.value[0],
            "magnitude": magnitude,
            "background": bkg_mean.value[0],
        }

    def get_state(self) -> None:
        pass

    def set_state(self, state: dict) -> None:
        pass
