from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from shutterbug.core.app_controller import AppController

from shutterbug.core.models import (
    FITSModel,
    StarMeasurement,
    GraphDataModel,
    StarIdentity,
)

from PySide6.QtGui import QUndoCommand

import logging


class RemoveMeasurementCommand(QUndoCommand):
    """Command to deselect a star"""

    def __init__(self, measurement: StarMeasurement, controller: AppController):
        super().__init__("Remove Measurements")
        self.measurement = measurement
        self.stars = controller.stars

    def redo(self):
        m = self.measurement
        logging.debug(
            f"COMMAND: Removing measurement at {m.x:.0f}/{m.y:.0f} for image {m.image_id}"
        )
        self.stars.unregister_measurement(m)

    def undo(self):
        m = self.measurement
        logging.debug(
            f"COMMAND: Undoing measurement removal at {m.x:.0f}/{m.y:.0f} for image {m.image_id}"
        )
        self.stars.register_measurement(m)


class RemoveStarCommand(QUndoCommand):
    """Command to deselect a star"""

    def __init__(self, star: StarIdentity, controller: AppController):
        super().__init__("Remove Measurements")
        self.star = star
        self.stars = controller.stars
        self.measurements = []

    def redo(self):
        s = self.star
        logging.debug(f"COMMAND: Removing star {s.id}")
        for m in s.measurements.copy().values():
            self.stars.unregister_measurement(m)
            self.measurements.append(m)

    def undo(self):
        logging.debug(f"COMMAND: Undoing star removal {self.star.id}")
        for m in self.measurements:
            self.stars.register_measurement(m, self.star)


class RemoveGraphCommand(QUndoCommand):
    """Command to deselect a star"""

    def __init__(self, measurement: StarMeasurement, controller: AppController):
        super().__init__("Remove Measurements")
        self.measurement = measurement
        self.stars = controller.stars

    def redo(self):
        m = self.measurement
        logging.debug(
            f"COMMAND: Removing measurement at {m.x:.0f}/{m.y:.0f} for image {m.image_id}"
        )
        self.stars.unregister_measurement(m)

    def undo(self):
        m = self.measurement
        logging.debug(
            f"COMMAND: Undoing measurement removal at {m.x:.0f}/{m.y:.0f} for image {m.image_id}"
        )
        self.stars.register_measurement(m)


class RemoveImageCommand(QUndoCommand):
    """Command to deselect a star"""

    def __init__(self, measurement: StarMeasurement, controller: AppController):
        super().__init__("Remove Measurements")
        self.measurement = measurement
        self.stars = controller.stars

    def redo(self):
        m = self.measurement
        logging.debug(
            f"COMMAND: Removing measurement at {m.x:.0f}/{m.y:.0f} for image {m.image_id}"
        )
        self.stars.unregister_measurement(m)

    def undo(self):
        m = self.measurement
        logging.debug(
            f"COMMAND: Undoing measurement removal at {m.x:.0f}/{m.y:.0f} for image {m.image_id}"
        )
        self.stars.register_measurement(m)
