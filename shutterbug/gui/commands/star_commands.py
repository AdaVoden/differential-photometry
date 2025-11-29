import logging
from typing import List
from PySide6.QtGui import QUndoCommand
from shutterbug.core.managers.star_catalog import StarCatalog
from shutterbug.core.models import FITSModel, StarMeasurement
from shutterbug.core.models.star_identity import StarIdentity


class AddMeasurementsCommand(QUndoCommand):
    """Command to select a star"""

    def __init__(self, stars: List, image: FITSModel):
        super().__init__()
        self.stars = stars
        self.image = image
        self.time = image.observation_time
        self.catalog = StarCatalog()
        self.measurements = []

    def redo(self):
        logging.debug(f"COMMAND: Adding {len(self.stars)} measurements")
        for star in self.stars:
            measurement = StarMeasurement(
                x=star["xcentroid"],
                y=star["ycentroid"],
                time=self.time,
                image=self.image.filename,
            )

            m = measurement
            self.catalog.register_measurement(m)
            self.measurements.append(m)

    def undo(self):
        logging.debug(f"COMMAND: undoing addition of {len(self.stars)} measurements")

        for m in self.measurements:

            self.catalog.unregister_measurement(m)


class RemoveMeasurementCommand(QUndoCommand):
    """Command to deselect a star"""

    def __init__(self, measurement: StarMeasurement):
        super().__init__()
        self.measurement = measurement
        self.catalog = StarCatalog()

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


class SelectStarCommand(QUndoCommand):

    def __init__(self, identity: StarIdentity):
        super().__init__()
        self.identity = identity
        self.catalog = StarCatalog()
        self.old_identity = self.catalog.active_star

    def redo(self):
        logging.debug(f"COMMAND: Setting active star to {self.identity.id}")
        self.catalog.set_active_star(self.identity)

    def undo(self):
        logging.debug(f"COMMAND: undoing selection of active star {self.identity.id}")
        self.catalog.set_active_star(self.old_identity)


class DeselectStarCommand(QUndoCommand):

    def __init__(self):
        super().__init__()
        self.catalog = StarCatalog()
        self.old_identity = self.catalog.active_star

    def redo(self):
        logging.debug(f"COMMAND: removing active star selection")
        self.catalog.set_active_star(None)

    def undo(self):
        logging.debug(f"COMMAND: undoing removal of active star")
        self.catalog.set_active_star(self.old_identity)
