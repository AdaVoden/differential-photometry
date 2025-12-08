#!/usr/bin/env python3

from shutterbug.core.models import StarMeasurement

from astropy.stats.sigma_clipping import sigma_clipped_stats

from photutils.aperture import CircularAnnulus, CircularAperture, aperture_photometry
from typing import Tuple, List

import numpy as np

# Photometry defaults
APERTURE_RADIUS_DEFAULT = 10  # pixels
ANNULUS_INNER_DEFAULT = 15  # pixels
ANNULUS_OUTER_DEFAULT = 20  # pixels
ZERO_POINT_DEFAULT = 25

# Error defaults
READ_NOISE_DEFAULT = 0
GAIN_DEFAULT = 1  # electrons/adu


def measure_star_magnitude(
    x: int,
    y: int,
    data,
    aperture_radius: float = APERTURE_RADIUS_DEFAULT,
    annulus_inner: float = ANNULUS_INNER_DEFAULT,
    annulus_outer: float = ANNULUS_OUTER_DEFAULT,
    gain: float = GAIN_DEFAULT,
    read_noise: float = READ_NOISE_DEFAULT,
    zero_point: float = ZERO_POINT_DEFAULT,
):
    """Measures the magnitude of a selected star"""
    # Define apertures
    position = [(x, y)]
    aperture = CircularAperture(position, r=aperture_radius)
    annulus = CircularAnnulus(position, r_in=annulus_inner, r_out=annulus_outer)

    # Measure flux
    phot_table = aperture_photometry(
        data, [aperture, annulus], method="subpixel", subpixels=3
    )

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
    magnitude, mag_error = _calculate_magnitude_with_error(
        flux_net_ADU, flux_err_ADU, zero_point
    )

    return magnitude, mag_error, flux_net_ADU, flux_err_ADU


def _calculate_magnitude_with_error(
    flux: float, flux_err: float, zero_point: float = ZERO_POINT_DEFAULT
) -> Tuple[float, float]:
    magnitude = -2.5 * np.log10(flux) + zero_point
    mag_error = (2.5 / np.log(10)) * (flux_err / flux)
    return magnitude, mag_error


def calculate_differential_magnitude(
    target_star: StarMeasurement, ref_stars: List[StarMeasurement]
):
    """Calculate differential magnitude on target image and stars"""
    # Make sure we're dealing with real data
    if target_star.mag_error is None:
        return target_star
    if target_star.mag is None:
        return target_star
    if len(ref_stars) < 1:
        return target_star
    ref_mags = [ref.mag for ref in ref_stars]
    ref_mags = np.asarray(ref_mags)
    ref_err = [ref.mag_error for ref in ref_stars]
    ref_err = np.asarray(ref_err)
    # (-ref_mags + target_mag) == target_mag - ref_mags
    target_star.diff_mag = float(np.mean((-1 * ref_mags) + target_star.mag))

    # Error calculation
    ref_err_rms = np.sqrt(ref_err**2 + target_star.mag_error**2)
    target_star.diff_err = float(np.sqrt(np.sum(ref_err_rms**2)) / len(ref_err_rms))

    return target_star
