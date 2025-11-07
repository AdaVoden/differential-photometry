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
            self.stars = {}  # id -> StarIdentity
            self._kdtree = None
            self._coords = []  # Reference coordinates
            self._ids = []  # Matching star IDs
            self._dirty = False
        return cls._instance

    def add_star(self, star_identity: StarIdentity, x: float, y: float):
        """Adds a star to the catalog"""
        self.stars[star_identity.id] = star_identity
        self._coords.append((x, y))
        self._ids.append(star_identity.id)
        self._dirty = True

    def _ensure_tree(self):
        """Rebuilds the KDTree for spacial coordinates"""
        if self._kdtree is None or self._dirty is True:
            # Generate new tree!
            self._kdtree = KDTree(self._coords)
        self._dirty = False

    def find_nearest(self, x: float, y: float, tolerance: float = 3.0):
        """Finds stars, if any, that exist at x/y position within tolerance"""
        self._ensure_tree()

        dist, idx = self._kdtree.query((x, y), distance_upper_bound=tolerance)

        if idx == self._kdtree.n:
            # Found nothing
            return None
        else:
            return self._ids[idx]

    def _new_id(self) -> int:
        if not self._ids:
            # No other stars available
            return 1
        last_id = self._ids[-1]
        return last_id + 1

    def register_measurement(
        self, measurement: StarMeasurement, is_target: bool, image_name: str
    ) -> StarIdentity:
        """Registers measurement with catalog"""
        match_id = self.find_nearest(measurement.x, measurement.y)
        if match_id:
            star = self.stars[match_id]
        else:
            star_id = f"star_{self._new_id}"
            star = StarIdentity(star_id, is_target)
            self.add_star(star, measurement.x, measurement.y)
        star.measurements[image_name] = measurement
        return star
