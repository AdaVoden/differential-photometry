from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from shutterbug.core.app_controller import AppController

from typing import Optional

from .base_observable import ObservableQObject

from uuid import uuid4


class StarMeasurement(ObservableQObject):
    """Measurement of a star within an image"""

    type = "measurement"

    def __init__(
        self,
        controller: AppController,
        x: float,
        y: float,
        time: float,
        image_id: str,
        flux: Optional[float] = None,
        flux_error: Optional[float] = None,
        mag: Optional[float] = None,
        mag_error: Optional[float] = None,
        diff_mag: Optional[float] = None,
        diff_err: Optional[float] = None,
    ):
        super().__init__(controller)
        # Intrinsic
        self.uid = uuid4().hex
        self.x = x
        self.y = y
        self.time = time
        self.image_id = image_id
        # Computed later
        self.flux = self._define_field("flux", flux)
        self.flux_error = self._define_field("flux_error", flux_error)
        self.mag = self._define_field("mag", mag)
        self.mag_error = self._define_field("mag_error", mag_error)
        self.diff_mag = self._define_field("diff_mag", diff_mag)
        self.diff_err = self._define_field("diff_err", diff_err)
