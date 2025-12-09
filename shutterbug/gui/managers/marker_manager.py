from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Slot
from PySide6.QtGui import QColor

if TYPE_CHECKING:
    from shutterbug.core.app_controller import AppController

from shutterbug.core.managers.base_manager import BaseManager
from shutterbug.core.models import MarkerModel, StarMeasurement, MarkerType
from shutterbug.core.events import Event, EventDomain


class MarkerManager(BaseManager):

    MARKER_COLOUR_DEFAULT = "magenta"
    MARKER_RADIUS_DEFAULT = 10  # pixels
    MARKER_THICKNESS_DEFAULT = 2  # pixels

    def __init__(self, controller: AppController, parent=None):
        super().__init__(controller, parent)
        self._markers = {}  # image.uid -> (x, y) -> [markers]

        self.controller.on("measurement.created", self.create_marker_from_measurement)

    def add_marker(self, marker: MarkerModel):
        """Adds marker to manager"""
        if marker.image_id not in self._markers:
            self._markers[marker.image_id] = {(marker.x, marker.y): [marker]}
        elif (marker.x, marker.y) not in self._markers[marker.image_id]:
            self._markers[marker.image_id][(marker.x, marker.y)] = [marker]
        else:
            self._markers[marker.image_id][(marker.x, marker.y)].append(marker)

        self.controller.dispatch(Event(EventDomain.MARKER, "created", data=marker))

    def remove_marker(self, marker: MarkerModel):
        """Removes marker from manager"""
        if marker.image_id not in self._markers:
            return  # No work to do

        if (marker.x, marker.y) not in self._markers[marker.image_id]:
            return  # No work to do again

        markers = self._markers[marker.image_id][(marker.x, marker.y)]
        if marker in markers:
            markers.remove(marker)
        # Clean up so manager doesn't balloon
        if len(markers) == 0:
            self._markers[marker.image_id].pop((marker.x, marker.y))
        if len(self._markers[marker.image_id]):
            self._markers.pop(marker.image_id)

        self.controller.dispatch(Event(EventDomain.MARKER, "removed", data=marker))

    @Slot(StarMeasurement)
    def create_marker_from_measurement(self, measurement: StarMeasurement):
        """Creates a marker from a star measurement"""
        marker = MarkerModel(
            measurement.image,
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
