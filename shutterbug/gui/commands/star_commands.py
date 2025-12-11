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
        super().__init__("Add Measurements")
        self.stars = stars
        self.image = image
        self.time = image.observation_time
        self.controller = controller
        self.old_select = None
        self.measurements = []

    def redo(self):
        logging.debug(f"COMMAND: Adding {len(self.stars)} measurements")
        for star in self.stars:
            measurement = self.controller.stars.create_measurement(
                star["xcentroid"],
                star["ycentroid"],
                self.image.observation_time,
                self.image.uid,
            )
            self.measurements.append(measurement)
        if len(self.measurements) == 1:
            self.old_select = self.controller.selections.star
            self.controller.selections.set_selected_object(self.measurements[0])

    def undo(self):
        logging.debug(f"COMMAND: undoing addition of {len(self.stars)} measurements")

        for m in self.measurements:

            self.controller.stars.unregister_measurement(m)

        if len(self.measurements) == 1:
            if self.old_select:
                self.controller.selections.set_selected_object(self.old_select)


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


class PhotometryMeasurementCommand(QUndoCommand):
    """Command to perform photometry on a star"""

    def __init__(
        self,
        measurements: List[StarMeasurement],
        image: FITSModel,
        parameters: PhotometryParameters,
        controller: AppController,
    ):
        super().__init__("Photometry")
        self.measurements = measurements
        self.image = image
        self.parameters = parameters
        self.controller = controller
        self.old = {}
        for m in self.measurements:
            self.old[m.uid] = {
                "flux": m.flux,
                "flux_error": m.flux_error,
                "mag": m.mag,
                "mag_error": m.mag_error,
            }

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
            o = self.old[m.uid]
            m.flux = o["flux"]
            m.flux_error = o["flux_error"]
            m.mag = o["mag"]
            m.mag_error = o["mag_error"]


class PhotometryAllCommand(QUndoCommand):
    """Runs photometry with parameters across all images"""

    def __init__(self, params: PhotometryParameters, controller: AppController):
        super().__init__("Photometry All Images")
        self.controller = controller
        self.params = params
        self.images = controller.images.get_all_images()
        self.cmds = []
        for i in self.images:
            measurements = controller.stars.get_measurements_by_image(i)
            self.cmds.append(
                PhotometryMeasurementCommand(
                    measurements, i, self.params, self.controller
                )
            )

    def redo(self):
        for cmd in self.cmds:
            cmd.redo()

    def undo(self):
        for cmd in self.cmds:
            cmd.undo()


class DifferentialPhotometryCommand(QUndoCommand):
    """Command to perform differential photometry on measurements"""

    def __init__(self, image: FITSModel, controller: AppController):
        super().__init__("Differential Photometry")
        self.image = image
        self.controller = controller
        self.measurements = controller.stars.get_measurements_by_image(image)
        self.old_measurements = {}
        # Take a snapshot
        for m in self.measurements:
            self.old_measurements[m.uid] = {
                "diff_mag": m.diff_mag,
                "diff_err": m.diff_err,
            }

    def redo(self):
        for m in self.measurements:
            other_ms = [n for n in self.measurements if n != m]
            phot.calculate_differential_magnitude(m, other_ms)

    def undo(self):
        # Reset to before times
        for m in self.measurements:
            m.diff_mag = self.old_measurements[m.uid]["diff_mag"]
            m.diff_err = self.old_measurements[m.uid]["diff_err"]


class DifferentialPhotometryAllCommand(QUndoCommand):
    """Command to perform differential photometry on all images' measurements"""

    def __init__(self, controller: AppController):
        super().__init__("Differential Photometry All Images")
        self.images = controller.images.get_all_images()
        self.cmds = []
        for i in self.images:
            self.cmds.append(DifferentialPhotometryCommand(i, controller))

    def redo(self):
        for cmd in self.cmds:
            cmd.redo()

    def undo(self):
        for cmd in self.cmds:
            cmd.undo()
