from PySide6.QtCore import QObject, Signal

from typing import Dict, Optional


class ObservableQObject(QObject):
    """Dataclass-like observable QObject"""

    updated = Signal(object)

    def _define_field(self, name, default):
        private_name = f"_{name}"
        setattr(self, private_name, default)

        def getter(self):
            return getattr(self, private_name)

        def setter(self, value):
            if value != getattr(self, private_name):
                setattr(self, private_name, value)
                self.updated.emit(self)

        setattr(self.__class__, name, property(getter, setter))


class StarMeasurement(ObservableQObject):
    """Measurement of a star within an image"""

    def __init__(
        self,
        x: float,
        y: float,
        time: float,
        image: str,
        flux: Optional[float] = None,
        flux_error: Optional[float] = None,
        mag: Optional[float] = None,
        mag_error: Optional[float] = None,
    ):
        super().__init__()
        # Intrinsic
        self.x = x
        self.y = y
        self.time = time
        self.image = image
        # Computed later
        self.flux = self._define_field("flux", flux)
        self.flux_error = self._define_field("flux_error", flux_error)
        self.mag = self._define_field("mag", mag)
        self.mag_error = self._define_field("mag_error", mag_error)


class StarIdentity(ObservableQObject):
    """Identity of star for cross-image synchronization"""

    id: str
    measurements: Dict[str, StarMeasurement] = {}  # Image name -> StarMeasurement
    use_in_ensemble: bool = True
    label: Optional[str] = None

    def __init__(
        self,
        id: str,
        measurements: Dict[str, StarMeasurement] = {},
        use_in_ensemble: bool = True,
        label: Optional[str] = None,
    ):
        super().__init__()
        self.id = id
        self.measurements = measurements
        self.use_in_ensemble = use_in_ensemble
        self.label = label
