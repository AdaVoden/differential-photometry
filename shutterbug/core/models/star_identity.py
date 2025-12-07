from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from shutterbug.core.app_controller import AppController

from typing import Dict, Optional
from uuid import uuid4

from .base_observable import ObservableQObject
from .star_measurement import StarMeasurement


class StarIdentity(ObservableQObject):
    """Identity of star for cross-image synchronization"""

    type = "star"

    def __init__(
        self,
        controller: AppController,
        id: str,
        use_in_ensemble: bool = True,
        label: Optional[str] = None,
    ):
        super().__init__(controller)
        self.uid = uuid4().hex
        self.id = id
        self.measurements: Dict[str, StarMeasurement] = {}
        self.use_in_ensemble = use_in_ensemble
        self.label = label
