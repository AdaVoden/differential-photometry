from PySide6.QtCore import Signal, QObject

from .star import StarMeasurement
from .star_catalog import StarCatalog

import logging


class StarManager(QObject):
    """Manager for an image's stars"""

    star_added = Signal(StarMeasurement)
    target_star_changed = Signal(StarMeasurement)
    star_removed = Signal(StarMeasurement)

    def __init__(self):
        super().__init__()

        self.stars = []  # Master star list
        self.star_coords = {}  # (x, y) -> StarMeasurement
        self._kdtree = None  # Spatial coordinate for lookups
        self._dirty = False
        self.catalog = StarCatalog()  # Singleton

    def add_star(self, star: StarMeasurement):
        """Add star measurement to manager"""
        self.stars.append(star)
        self.star_coords[(round(star.x), round(star.y))] = star
        self.star_added.emit(star)

    def remove_star(self, star: StarMeasurement):
        """Remove star measurement from manager"""
        pass

    def _ensure_tree(self):
        """Create or rebuild the KDTree for spacial detection"""
        pass

    def find_nearest(self, x: float, y: float, tolerance: float = 3.0):
        """Finds the nearest star from coordinate"""
        pass
