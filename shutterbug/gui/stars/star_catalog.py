import logging

from .star import StarIdentity


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
            self._coords = []
            self._ids = []
            self._dirty = False
        return cls._instance

    def add_star(self, star_identity: StarIdentity, x: float, y: float):
        """Adds a star to the catalog"""
        pass

    def _ensure_tree(self):
        """Rebuilds the KDTree for spacial coordinates"""
        pass

    def find_near(self, x: float, y: float, tolerance: float = 3.0):
        """Finds stars, if any, that exist at x/y position within tolerance"""
        pass

    def register_measurement(self, x: float, y: float, image_name: str):
        """Registers measurement with catalog"""
        pass
