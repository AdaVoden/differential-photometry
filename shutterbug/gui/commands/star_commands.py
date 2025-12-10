from __future__ import annotations

from typing import TYPE_CHECKING

from shutterbug.gui.operators.operator_parameters import PhotometryParameters

if TYPE_CHECKING:
    from shutterbug.core.app_controller import AppController

import logging
from typing import List
from PySide6.QtGui import QUndoCommand
from shutterbug.core.models import FITSModel, StarMeasurement
import shutterbug.core.utility.photometry as phot


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
                image_id=self.image.uid,
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
        self.stars = controller.stars

    def redo(self):
        m = self.measurement
        logging.debug(
            f"COMMAND: Removing measurement at {m.x:.0f}/{m.y:.0f} for image {m.image}"
        )
        self.stars.unregister_measurement(m)

    def undo(self):
        m = self.measurement
        logging.debug(
            f"COMMAND: Undoing measurement removal at {m.x:.0f}/{m.y:.0f} for image {m.image}"
        )
        self.stars.register_measurement(m)


class PhotometryMeasurementCommand(QUndoCommand):
    """Command to perform photometry on a star"""

    def __init__(
        self,
        measurements: List[StarMeasurement],
        image: FITSModel,
        parameters: PhotometryParameters,
        controller: AppController,
    ):
        super().__init__()
        self.measurements = measurements
        self.image = image
        self.parameters = parameters
        self.controller = controller

    def redo(self):
        for m in self.measurements:
            data = self.image.get_stamp(
                m.x, m.y, r=self.parameters.annulus_outer_radius
            )
            # star is in middle of data
            x = data.shape[0] / 2
            y = x
            mag, mag_err, flux, flux_err = phot.measure_star_magnitude(
                x=x,
                y=y,
                data=data,
                aperture_radius=self.parameters.aperture_radius,
                annulus_inner=self.parameters.annulus_inner_radius,
                annulus_outer=self.parameters.annulus_outer_radius,
            )
            m.mag = mag
            m.mag_error = mag_err
            m.flux = flux
            m.flux_error = flux_err

    def undo(self):
        for m in self.measurements:
            m.flux = None
            m.flux_error = None
            m.mag = None
            m.mag_error = None
