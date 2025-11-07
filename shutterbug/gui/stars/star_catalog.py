import logging

from .star import StarIdentity, StarMeasurement

from scipy.spatial import KDTree


class StarCatalog:
    """Catalogues stars between images. Is a singleton."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            logging.debug("Creating Star Catalog singleton")
            cls._instance = super(StarCatalog, cls).__new__(cls)
            # initial variables
            cls.stars = {}  # id -> StarIdentity
            cls._kdtree = None
            cls._coords = []  # Reference coordinates
            cls._ids = []  # Matching star IDs
            cls._dirty = False
        return cls._instance

    def add_star(self, star_identity: StarIdentity, x: float, y: float):
        """Adds a star to the catalog"""
        self.stars[star_identity.id] = star_identity
        self._coords.append((x, y))
        self._ids.append(star_identity.id)
        self._dirty = True

    def remove_star(self, star_identity: StarIdentity, x: float, y: float):
        """Removes stars from the catalog"""
        self.stars.pop(star_identity.id)
        self._coords.remove((x, y))
        self._ids.remove(star_identity.id)
        self._dirty = True

    def _ensure_tree(self):
        """Rebuilds the KDTree for spacial coordinates"""
        if self._kdtree is None or self._dirty is True:
            if not self._coords:
                self._kdtree = None
                return
            # Generate new tree!
            self._kdtree = KDTree(self._coords)
        self._dirty = False

    def find_nearest(self, x: float, y: float, tolerance: float = 3.0):
        """Finds stars, if any, that exist at x/y position within tolerance"""
        self._ensure_tree()

        if self._kdtree is None:
            return None

        dist, idx = self._kdtree.query((x, y), distance_upper_bound=tolerance)

        if idx == self._kdtree.n:
            # Found nothing
            return None
        else:
            return self._ids[idx]

    def _new_id(self) -> int:
        """Creates a new ID for a StarIdentity"""
        if not self._ids:
            # No other stars available
            return 1
        last_id = self._ids[-1]
        return last_id + 1

    def register_measurement(self, measurement: StarMeasurement) -> StarIdentity:
        """Registers measurement with catalog"""
        match_id = self.find_nearest(measurement.x, measurement.y)
        if match_id:
            star = self.stars[match_id]
        else:
            star_id = f"star_{self._new_id}"
            star = StarIdentity(id=star_id)
            self.add_star(star, measurement.x, measurement.y)
        star.measurements[measurement.image] = measurement
        return star

    def unregister_measurement(self, measurement: StarMeasurement):
        """Removes measurement from star in catalog"""
        match_id = self.find_nearest(measurement.x, measurement.y)
        if match_id:
            star = self.stars[match_id]
            star.measurements.pop(measurement.image)
            if len(star.measurements) == 0:
                self.remove_star(star, measurement.x, measurement.y)
                return
