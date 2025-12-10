from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Slot
from PySide6.QtGui import QColor

from shutterbug.core.models.fits_model import FITSModel

if TYPE_CHECKING:
    from shutterbug.core.app_controller import AppController

from shutterbug.core.managers.base_manager import BaseManager
from shutterbug.core.models import MarkerModel, MarkerType
from shutterbug.core.events import Event, EventDomain

import logging


class MarkerManager(BaseManager):

    MARKER_COLOUR_DEFAULT = "magenta"
    MARKER_RADIUS_DEFAULT = 10  # pixels
    MARKER_THICKNESS_DEFAULT = 2  # pixels

    def __init__(self, controller: AppController, parent=None):
        super().__init__(controller, parent)
        self._markers = {}  # image.uid -> [markers]

        self.controller.on("measurement.created", self._on_measurement_created)

        logging.debug("Marker manager initialized")

    def add_marker(self, marker: MarkerModel):
        """Adds marker to manager"""
        if marker.image_id not in self._markers:
            self._markers[marker.image_id] = [marker]
        else:
            self._markers[marker.image_id].append(marker)

        self.controller.dispatch(Event(EventDomain.MARKER, "created", data=marker))
        logging.debug(f"Added marker {marker.id}")

    def remove_marker(self, marker: MarkerModel):
        """Removes marker from manager"""
        if marker.image_id not in self._markers:
            return  # No work to do

        if marker in self._markers[marker.image_id]:
            self._markers[marker.image_id].remove(marker)

        # Clean up so manager doesn't balloon
        if len(self._markers[marker.image_id]) == 0:
            self._markers.pop(marker.image_id)

        self.controller.dispatch(Event(EventDomain.MARKER, "removed", data=marker))
        logging.debug(f"Removed marker: {marker.id}")

    @Slot(Event)
    def _on_measurement_created(self, event: Event):
        """Creates a marker from a star measurement"""
        measurement = event.data
        if measurement is None:
            logging.error("No measurement provided on measurement created event")
            return  # No measurement provided
        marker = MarkerModel(
            measurement.image_id,
            measurement.x,
            measurement.y,
            MarkerType.DISPLAY,
            self.MARKER_RADIUS_DEFAULT,
            QColor(self.MARKER_COLOUR_DEFAULT),
            self.MARKER_THICKNESS_DEFAULT,
            True,
            self.controller,
        )
        self.add_marker(marker)

    def create_marker_from_position(self, x: float, y: float, image: FITSModel):
        """Given a position, create a default marker in image"""
        marker = self.create(
            image.uid,
            x,
            y,
            MarkerType.DISPLAY,
            self.MARKER_RADIUS_DEFAULT,
            self.MARKER_COLOUR_DEFAULT,
            self.MARKER_THICKNESS_DEFAULT,
        )
        return marker

    def create(
        self,
        image_id: str,
        x: float,
        y: float,
        type: MarkerType,
        radius: float,
        colour: str,
        thickness: int,
    ):
        """Creates a marker and adds it to the system"""
        marker = MarkerModel(
            image_id,
            x,
            y,
            MarkerType(type),
            radius,
            QColor(colour),
            thickness,
            True,
            self.controller,
        )
        self.add_marker(marker)
        return marker

    def markers_from_image(self, image: FITSModel):
        """Returns all markers associated with image"""
        if image.uid in self._markers:
            return self._markers[image.uid]
        return []
