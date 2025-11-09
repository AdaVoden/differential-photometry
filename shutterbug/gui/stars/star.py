from pydantic import BaseModel

from PySide6.QtCore import QObject, Signal

from typing import Dict, Optional


class StarMeasurement(QObject, BaseModel):
    """Measurement of a star within an image"""

    updated = Signal(object)

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

    def __init__(self, **kwargs):
        QObject.__init__(self)
        BaseModel.__init__(self, **kwargs)

    def __setattr__(self, name, value):
        # Pydantic can still do its thing
        old_value = getattr(self, name, None)
        super().__setattr__(name, value)
        # And we can emit a signal when changed
        if name in StarMeasurement.model_fields and old_value != value:
            self.updated.emit(self)


class StarIdentity(BaseModel):
    """Identity of star for cross-image synchronization"""

    id: str
    measurements: Dict[str, StarMeasurement] = {}  # Image name -> StarMeasurement
    use_in_ensemble: bool = True
    label: Optional[str] = None
