import logging
from typing import List

from PySide6.QtCore import QObject, Signal
from scipy.spatial import KDTree

from shutterbug.core.models import StarMeasurement, MeasurementMetadataModel
from shutterbug.core.managers import StarCatalog


class MeasurementManager(QObject):
    """Manager for all star measurements"""

    _instance = None

    measurement_added = Signal(StarMeasurement)
    measurement_changed = Signal(object)
    measurement_removed = Signal(StarMeasurement)

    def __init__(self):
        if not hasattr(self, "_initialized"):
            self._initialized = True
            super().__init__()

            self.metadata = {}  # image -> metadata
            self.catalog = StarCatalog()  # Singleton

    def __new__(cls):
        if cls._instance is None:
            logging.debug("Creating MeasurementManager singleton")
            cls._instance = super().__new__(cls)

    def add_measurement(self, measurement: StarMeasurement):
        """Add star measurement to manager"""
        metadata = self.metadata.get(measurement.image)
        if metadata is None:
            metadata = MeasurementMetadataModel(measurement.image)
            self.metadata[measurement.image] = metadata
        coords = (round(measurement.x), round(measurement.y))
        metadata.stars[coords] = measurement
        metadata.star_coordinates.append((measurement.x, measurement.y))
        metadata.is_dirty = True
        id = self.catalog.register_measurement(measurement)
        logging.debug(f"Added measurement to star: {id.id}")
        self.measurement_added.emit(measurement)
        # If the star changes, alert everything
        measurement.updated.connect(self.measurement_changed)

    def remove_measurement(self, measurement: StarMeasurement):
        """Remove star measurement from manager"""
        metadata = self.metadata.get(measurement.image)
        if metadata is None:
            return  # No work to do!
        coords = (round(measurement.x), round(measurement.y))
        metadata.star_coords.remove((measurement.x, measurement.y))
        metadata.stars.pop(coords)
        metadata.dirty = True
        self.catalog.unregister_measurement(measurement)
        logging.debug(f"Removed measurement: {measurement}")
        self.measurement_removed.emit(measurement)
        measurement.updated.disconnect(self.measurement_changed)

    def _ensure_tree(self, metadata: MeasurementMetadataModel):
        """Create or rebuild the KDTree for spacial detection"""
        kdtree = metadata.kdtree
        dirty = metadata.is_dirty
        if kdtree is None or dirty is True:
            if not metadata.star_coordinates:
                self._kdtree = None
                return
            # Generate new tree!
            logging.debug(
                f"StarManager rebuilt KDTree with {len(metadata.star_coordinates)} coordinates"
            )
            self._kdtree = KDTree(metadata.star_coordinates)
        self._dirty = False

    def find_nearest(self, image_name: str, x: float, y: float, tolerance: float = 3.0):
        """Finds the nearest star from coordinate"""
        metadata = self.metadata.get(image_name)
        if metadata is None:
            return None

        self._ensure_tree(metadata)
        if self._kdtree is None:
            return None

        _, idx = self._kdtree.query((x, y), distance_upper_bound=tolerance)

        if idx == self._kdtree.n:
            # Found nothing
            return None
        else:
            pure_coords = metadata.star_coordinates[idx]
            coords = (round(pure_coords[0]), round(pure_coords[1]))
            return metadata.stars[coords]

    def get_all_stars(self, image_name: str) -> List:
        """Gets all stars from the manager"""
        metadata = self.metadata.get(image_name)
        if metadata is None:
            return []
        return list(metadata.stars.values())
