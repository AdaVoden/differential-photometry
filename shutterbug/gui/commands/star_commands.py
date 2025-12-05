from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from shutterbug.core.app_controller import AppController

import logging
from typing import List
from PySide6.QtGui import QUndoCommand
from shutterbug.core.models import FITSModel, StarMeasurement


class AddMeasurementsCommand(QUndoCommand):
    """Command to select a star"""

    def __init__(self, stars: List, image: FITSModel, controller: AppController):
        super().__init__()
        self.stars = stars
        self.image = image
        self.time = image.observation_time
        self.controller = controller
        self.measurements = []

    def redo(self):
        logging.debug(f"COMMAND: Adding {len(self.stars)} measurements")
        for star in self.stars:
            measurement = StarMeasurement(
                controller=self.controller,
                x=star["xcentroid"],
                y=star["ycentroid"],
                time=self.time,
                image=self.image.filename,
            )

            self.controller.stars.register_measurement(measurement)
            self.measurements.append(measurement)

    def undo(self):
        logging.debug(f"COMMAND: undoing addition of {len(self.stars)} measurements")

        for m in self.measurements:

            self.controller.stars.unregister_measurement(m)


class RemoveMeasurementCommand(QUndoCommand):
    """Command to deselect a star"""

    def __init__(self, measurement: StarMeasurement, controller: AppController):
        super().__init__()
        self.measurement = measurement
        self.catalog = controller.stars

    def redo(self):
        m = self.measurement
        logging.debug(
            f"COMMAND: Removing measurement at {m.x:.0f}/{m.y:.0f} for image {m.image}"
        )
        self.catalog.unregister_measurement(m)

    def undo(self):
        m = self.measurement
        logging.debug(
            f"COMMAND: Undoing measurement removal at {m.x:.0f}/{m.y:.0f} for image {m.image}"
        )
        self.catalog.register_measurement(m)
