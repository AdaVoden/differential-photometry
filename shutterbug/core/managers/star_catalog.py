import logging

from PySide6.QtCore import QObject, Signal
from scipy.spatial import KDTree
from shutterbug.core.models import StarIdentity, StarMeasurement


class StarCatalog(QObject):
    """Catalogues stars between images. Is a singleton."""

    _instance = None
    star_added = Signal(StarIdentity)
    star_removed = Signal(StarIdentity)
    active_star_changed = Signal(StarIdentity)

    def __new__(cls):
        if cls._instance is None:
            logging.debug("Creating Star Catalog singleton")
            cls._instance = super(StarCatalog, cls).__new__(cls)
            # initial variables
            cls.stars = {}  # id -> StarIdentity
            cls.measurement_to_star = {}  # StarMeasurement -> StarIdentity
            cls.active_star = None  # selected star
            cls._kdtree = None
            cls._coords = []  # Reference coordinates
            cls._ids = []  # Matching star IDs
            cls._dirty = False

        return cls._instance

    def _add_star(self, star_identity: StarIdentity, x: float, y: float):
        """Adds a star to the catalog"""
        self.stars[star_identity.id] = star_identity
        self._coords.append((x, y))
        self._ids.append(star_identity.id)
        self._dirty = True
        self.star_added.emit(star_identity)
        logging.debug(f"Added identity: {star_identity.id}")

    def _remove_star(self, star_identity: StarIdentity, x: float, y: float):
        """Removes stars from the catalog"""
        self.stars.pop(star_identity.id)
        self._coords.remove((x, y))
        self._ids.remove(star_identity.id)
        self._dirty = True
        self.star_removed.emit(star_identity)
        logging.debug(f"Removed identity: {star_identity.id}")

    def _ensure_tree(self):
        """Rebuilds the KDTree for spacial coordinates"""
        if self._kdtree is None or self._dirty is True:
            if not self._coords:
                self._kdtree = None
                return
            # Generate new tree!
            logging.debug(
                f"StarCatalog rebuilt KDTree with {len(self._coords)} coordinates"
            )
            self._kdtree = KDTree(self._coords)
        self._dirty = False

    def find_nearest(self, x: float, y: float, tolerance: float = 3.0):
        """Finds stars, if any, that exist at x/y position within tolerance"""
        self._ensure_tree()

        if self._kdtree is None:
            return None

        _, idx = self._kdtree.query((x, y), distance_upper_bound=tolerance)

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
        last_id_str = self._ids[-1].split("_")[1]
        last_id = int(last_id_str)
        return last_id + 1

    def register_measurement(self, measurement: StarMeasurement) -> StarIdentity:
        """Registers measurement with catalog"""
        match_id = self.find_nearest(measurement.x, measurement.y)
        if match_id:
            star = self.stars[match_id]
        else:
            star_id = f"Star_{self._new_id()}"
            star = StarIdentity(id=star_id)
            self._add_star(star, measurement.x, measurement.y)
        star.measurements[measurement.image] = measurement
        self.measurement_to_star[measurement] = star
        return star

    def unregister_measurement(self, measurement: StarMeasurement) -> None:
        """Removes measurement from star in catalog"""
        match_id = self.find_nearest(measurement.x, measurement.y)
        if match_id:
            star = self.stars[match_id]
            star.measurements.pop(measurement.image)
            self.measurement_to_star.pop(measurement)
            if len(star.measurements) == 0:
                self._remove_star(star, measurement.x, measurement.y)
                return

    def get_by_measurement(self, measurement: StarMeasurement) -> StarIdentity | None:
        """Retreives a star's identity by a measurement, if any"""
        if measurement in self.measurement_to_star:
            return self.measurement_to_star[measurement]
        else:
            return None

    def set_active_star(self, star: StarIdentity | None):
        """Sets active star"""
        if self.active_star != star:
            if star is None:
                logging.debug(f"Setting active star to none")
            else:
                logging.debug(f"Setting star as active: {star.id}")
            self.active_star = star
            self.active_star_changed.emit(star)
