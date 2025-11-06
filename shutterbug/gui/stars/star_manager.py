from PySide6.QtCore import Signal, QObject

from .star import StarMeasurement
from .star_catalog import StarCatalog

import logging


class StarManager(QObject):
    """Manager for an image's stars"""

    star_added = Signal(StarMeasurement)
    target_star_changed = Signal(SelectedStar)
    star_removed = Signal(StarMeasurement)

    def __init__(self):
        super().__init__()

        self.stars = []  # Master star list
        self.star_coords = {}  # (x, y) -> StarMeasurement
        self._kdtree  # Spatial coordinate for lookups
        self._dirty = False
        self.catalog = StarCatalog()  # Singleton

    def add_star(self, star: StarMeasurement):
        pass

    def remove_star(self, star: StarMeasurement):
        pass

    def _ensure_tree(self):
        pass

    def find_nearest(self, x: float, y: float):
        pass
