#!/usr/bin/env python3

from typing import Dict, Optional
from uuid import uuid4

from .base_observable import ObservableQObject
from .star_measurement import StarMeasurement


class StarIdentity(ObservableQObject):
    """Identity of star for cross-image synchronization"""

    def __init__(
        self,
        id: str,
        measurements: Dict[str, StarMeasurement] = {},
        use_in_ensemble: bool = True,
        label: Optional[str] = None,
    ):
        super().__init__()
        self.uid = uuid4().hex
        self.id = id
        self.measurements = measurements
        self.use_in_ensemble = use_in_ensemble
        self.label = label
