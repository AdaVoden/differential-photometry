from __future__ import annotations

from typing import TYPE_CHECKING

from shutterbug.core.events.change_event import (
    Event,
    EventDomain,
)

if TYPE_CHECKING:
    from shutterbug.core.app_controller import AppController

import logging
from typing import Dict, List

from scipy.spatial import KDTree
from shutterbug.core.models import StarIdentity, StarMeasurement

from .base_manager import BaseManager


class StarCatalog(BaseManager):
    """Catalogues stars between images. Is a singleton."""

    def __init__(self, controller: AppController, parent=None):
        super().__init__(controller, parent)
        self.stars: Dict[str, StarIdentity] = {}  # id -> StarIdentity
        self.measurement_to_star: Dict[str, StarIdentity] = (
            {}
        )  # StarMeasurement.uid -> StarIdentity
        self.active_star = None  # selected star
        self._kdtree = None
        self._coords = []  # Reference coordinates
        self._ids = []  # Matching star IDs
        self._dirty = False

        logging.debug("Star Catalog initialized")

    def _add_star(self, star_identity: StarIdentity, x: float, y: float):
        """Adds a star to the catalog"""
        self.stars[star_identity.id] = star_identity
        self._coords.append((x, y))
        self._ids.append(star_identity.id)
        self._dirty = True
        self.controller.dispatch(Event(EventDomain.STAR, "created", data=star_identity))
        logging.debug(f"Added identity: {star_identity.id}")

    def _remove_star(self, star_identity: StarIdentity, x: float, y: float):
        """Removes stars from the catalog"""
        self.stars.pop(star_identity.id)
        self._coords.remove((x, y))
        self._ids.remove(star_identity.id)
        self._dirty = True
        self.controller.dispatch(Event(EventDomain.STAR, "removed", data=star_identity))
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

    def find_nearest(
        self, x: float, y: float, tolerance: float = 3.0
    ) -> StarIdentity | None:
        """Finds stars, if any, that exist at x/y position within tolerance"""
        self._ensure_tree()

        if self._kdtree is None:
            return None

        _, idx = self._kdtree.query((x, y), distance_upper_bound=tolerance)

        if idx == self._kdtree.n:
            # Found nothing
            return None
        else:
            return self.stars[self._ids[idx]]

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
        star = self.find_nearest(measurement.x, measurement.y)
        if star is None:
            star_id = f"Star_{self._new_id()}"
            star = StarIdentity(controller=self.controller, id=star_id)
            self._add_star(star, measurement.x, measurement.y)
        star.measurements[measurement.image_id] = measurement
        self.measurement_to_star[measurement.uid] = star
        self.controller.dispatch(
            Event(EventDomain.MEASUREMENT, "created", data=measurement)
        )
        return star

    def unregister_measurement(self, measurement: StarMeasurement) -> None:
        """Removes measurement from star in catalog"""
        star = self.find_nearest(measurement.x, measurement.y)
        if star is not None:
            star.measurements.pop(measurement.image_id)
            self.measurement_to_star.pop(measurement.uid)
            self.controller.dispatch(
                Event(EventDomain.MEASUREMENT, "removed", data=measurement)
            )
            if len(star.measurements) == 0:
                self._remove_star(star, measurement.x, measurement.y)
                return

    def get_by_measurement(self, measurement: StarMeasurement) -> StarIdentity | None:
        """Retreives a star's identity by a measurement, if any"""
        if measurement.uid in self.measurement_to_star:
            return self.measurement_to_star[measurement.uid]
        else:
            return None

    def get_measurements_by_image(self, image_name: str) -> List[StarMeasurement]:
        """Gets all measurements that belong to a specific image"""
        measurements = []
        for star in self.get_all_stars():
            m = star.measurements.get(image_name)
            if m is not None:
                measurements.append(m)
        return measurements

    def get_all_stars(self) -> List[StarIdentity]:
        """Gets all stars currently registered"""
        return list(self.stars.values())
