#!/usr/bin/env python3


from typing import Dict, List, Tuple

from scipy.spatial import KDTree
from shutterbug.core.models.star_measurement import StarMeasurement


class MeasurementMetadataModel:
    """Measurement manager data and lookup model"""

    def __init__(self, image: str):

        self.image: str = image
        # x/y coordinates
        self.star_coordinates: List[Tuple[float, float]] = []
        # x/y -> StarMeasurement
        self.stars: Dict[Tuple[int, int], StarMeasurement] = {}
        # coordinate lookup
        self.kdtree: KDTree | None = None
        # if the kdtree is dirty or not
        self.is_dirty: bool = False
