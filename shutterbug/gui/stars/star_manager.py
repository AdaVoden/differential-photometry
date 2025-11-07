from PySide6.QtCore import Signal, QObject

from .star import StarMeasurement
from .star_catalog import StarCatalog

from scipy.spatial import KDTree

import logging


class StarManager(QObject):
    """Manager for an image's stars"""

    star_added = Signal(StarMeasurement)
    target_star_changed = Signal(StarMeasurement)
    star_removed = Signal(StarMeasurement)

    def __init__(self):
        super().__init__()

        self.star_coords = []  # Master coord list
        self.stars = {}  # (x, y) -> StarMeasurement
        self._kdtree = None  # Spatial coordinate for lookups
        self._dirty = False
        self.catalog = StarCatalog()  # Singleton

    def add_star(self, star: StarMeasurement):
        """Add star measurement to manager"""
        coords = (round(star.x), round(star.y))
        self.stars[coords] = star
        self.star_coords.append((star.x, star.y))
        self._dirty = True
        self.star_added.emit(star)

    def remove_star(self, star: StarMeasurement):
        """Remove star measurement from manager"""
        coords = (round(star.x), round(star.y))
        self.star_coords.remove((star.x, star.y))
        self.stars.pop(coords)
        self._dirty = True
        self.star_removed.emit(star)

    def _ensure_tree(self):
        """Create or rebuild the KDTree for spacial detection"""
        if self._kdtree is None or self._dirty is True:
            if not self.star_coords:
                self._kdtree = None
                return
            # Generate new tree!
            self._kdtree = KDTree(self.star_coords)
        self._dirty = False

    def find_nearest(self, x: float, y: float, tolerance: float = 3.0):
        """Finds the nearest star from coordinate"""
        self._ensure_tree()
        if self._kdtree is None:
            return None

        dist, idx = self._kdtree.query((x, y), distance_upper_bound=tolerance)

        if idx == self._kdtree.n:
            # Found nothing
            return None
        else:
            pure_coords = self.star_coords[idx]
            coords = (round(pure_coords[0]), round(pure_coords[1]))
            return self.stars[coords]
