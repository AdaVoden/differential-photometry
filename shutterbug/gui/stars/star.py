from pydantic import BaseModel

from typing import Dict


class StarMeasurement(BaseModel):
    """Measurement of a star within an image"""

    x: int
    y: int
    flux: float
    fwhm: float | None
    magnitude: float | None
    mag_error: float | None


class StarIdentity(BaseModel):
    """Identity of star for cross-image synchronization"""

    id: int
    is_target: bool
    measurements: Dict[str, StarMeasurement]  # Image name -> StarMeasurement
