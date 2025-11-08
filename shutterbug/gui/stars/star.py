from pydantic import BaseModel

from typing import Dict, Optional


class StarMeasurement(BaseModel):
    """Measurement of a star within an image"""

    # Intrinsic
    x: float
    y: float
    time: float
    image: str
    # Calculated from measurement
    flux: Optional[float] = None
    flux_error: Optional[float] = None
    fwhm: Optional[float] = None
    mag: Optional[float] = None
    mag_error: Optional[float] = None


class StarIdentity(BaseModel):
    """Identity of star for cross-image synchronization"""

    id: str
    measurements: Dict[str, StarMeasurement] = {}  # Image name -> StarMeasurement
    use_in_ensemble: bool = True
    label: Optional[str] = None
