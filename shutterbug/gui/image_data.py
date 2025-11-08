from pathlib import Path

from astropy.stats.sigma_clipping import sigma_clipped_stats
import numpy as np
from astropy import stats
from photutils.aperture import CircularAnnulus, CircularAperture, aperture_photometry
from photutils.detection import DAOStarFinder
from PySide6.QtCore import QObject, Signal
from .stars import StarMeasurement, MeasurementManager

from typing import Tuple


class FITSImage(QObject):
    """FITS image data and display class"""

    brightness_changed = Signal(int)
    contrast_changed = Signal(int)

    # Photometry defaults
    APERTURE_RADIUS_DEFAULT = 10  # pixels
    ANNULUS_INNER_DEFAULT = 15  # pixels
    ANNULUS_OUTER_DEFAULT = 20  # pixels
    ZERO_POINT_DEFAULT = 25

    # Error defaults
    READ_NOISE_DEFAULT = 0
    GAIN_DEFAULT = 1  # electrons/adu

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

        # Star manager per image
        self.star_manager = MeasurementManager()

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

    def compute_background(self):
        """Calculate background of image using sigma-clipped statistics"""

        _, median, _ = stats.sigma_clipped_stats(self.original_data, sigma=self.sigma)
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

    def measure_star_magnitude(
        self,
        star: StarMeasurement,
        aperture_radius: int = APERTURE_RADIUS_DEFAULT,
        annulus_inner: int = ANNULUS_INNER_DEFAULT,
        annulus_outer: int = ANNULUS_OUTER_DEFAULT,
        gain: float = GAIN_DEFAULT,
        read_noise: float = READ_NOISE_DEFAULT,
    ):
        """Measures the magnitude of a selected star"""
        # Define apertures
        position = [(star.x, star.y)]
        aperture = CircularAperture(position, r=aperture_radius)
        annulus = CircularAnnulus(position, r_in=annulus_inner, r_out=annulus_outer)

        # Measure flux
        data = self.original_data
        phot_table = aperture_photometry(data, [aperture, annulus], method="exact")

        # Photometry sums
        flux_aperture_ADU = phot_table["aperture_sum_0"][0]
        # annulus_sum_ADU = phot_table["aperture_sum_1"][0]

        ann_mask = annulus.to_mask(method="exact")

        ann_vals = []
        for mask in ann_mask:
            arr = mask.multiply(data)

            weights = mask.data

            valid = weights > 0
            if np.any(valid):
                # unweighted distribution of pixels
                ann_vals.extend((arr[valid] / weights[valid]).ravel().tolist())

        if len(ann_vals) == 0:
            # Fallback on global background
            _, median_bkg, std_bkg = sigma_clipped_stats(data)
        else:
            _, median_bkg, std_bkg = sigma_clipped_stats(ann_vals)

        # Background per pixel
        bkg_per_pix_ADU = median_bkg
        bkg_rms_ADU = std_bkg

        # Background-subtracted flux inside aperture
        bkg_total_ap_ADU = bkg_per_pix_ADU * aperture.area

        # background-subtracted flux in ADU
        flux_net_ADU = flux_aperture_ADU - bkg_total_ap_ADU

        # to electrons
        flux_net_e = flux_net_ADU * gain
        sigma_bkg_e = bkg_rms_ADU * gain

        # Variance
        var_shot = max(flux_net_e, 0.0)  # Poisson noise in e, clip negatives to 0
        var_bkg = aperture.area * (sigma_bkg_e**2)
        var_bkg_mean = (aperture.area**2 / max(1.0, annulus.area)) * (sigma_bkg_e**2)
        var_read = aperture.area * (read_noise**2)

        var_total_e = var_shot + var_bkg + var_bkg_mean + var_read
        sigma_total_e = np.sqrt(var_total_e)

        flux_err_ADU = sigma_total_e / gain

        # Convert to magnitude
        magnitude, mag_error = self._calculate_magnitude_with_error(
            flux_net_ADU, flux_err_ADU, self.zero_point
        )

        star.mag = magnitude
        star.mag_error = mag_error
        star.flux = flux_net_ADU
        star.flux_error = flux_err_ADU

        return star

    def _calculate_magnitude_with_error(
        self, flux: float, flux_err: float, zero_point: float = ZERO_POINT_DEFAULT
    ) -> Tuple[float, float]:
        magnitude = -2.5 * np.log10(flux) + zero_point
        mag_error = (2.5 / np.log(10)) * (flux_err / flux)
        return magnitude, mag_error

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
