from photutils.aperture import CircularAperture, CircularAnnulus, aperture_photometry

import numpy as np


def measure_star_magnitude(
    self,
    star_x: float,
    star_y: float,
    aperture_radius: int = 10,
    annulus_inner: int = 15,
    annulus_outer: int = 20,
):
    """Measure the instrumental magnitude of a star"""

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

    return {
        "flux": star_flux.value[0],
        "magnitude": magnitude,
        "background": bkg_mean.value[0],
    }
