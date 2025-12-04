from typing import Optional

from PySide6.QtCore import Signal

from shutterbug.core.events.change_event import MeasurementUpdateEvent

from .base_observable import ObservableQObject

from uuid import uuid4


class StarMeasurement(ObservableQObject):
    """Measurement of a star within an image"""

    updated = Signal(MeasurementUpdateEvent)

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
        diff_mag: Optional[float] = None,
        diff_err: Optional[float] = None,
    ):
        super().__init__()
        # Intrinsic
        self.uid = uuid4().hex
        self.x = x
        self.y = y
        self.time = time
        self.image = image
        # Computed later
        self.flux = self._define_field("flux", flux)
        self.flux_error = self._define_field("flux_error", flux_error)
        self.mag = self._define_field("mag", mag)
        self.mag_error = self._define_field("mag_error", mag_error)
        self.diff_mag = self._define_field("diff_mag", diff_mag)
        self.diff_err = self._define_field("diff_err", diff_err)
