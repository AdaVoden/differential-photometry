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
                flux=star["flux"],
                mag=star["mag"],
            )
            self.measurements.append(measurement)
        if len(self.measurements) == 1:
            self.star_select = self.controller.stars.get_by_measurement(
                self.measurements[0]
            )

            if self.star_select:
                self.old_select = self.controller.selections.star
                self.controller.selections.select(self.star_select)

    def undo(self):
        logging.debug(f"COMMAND: undoing addition of {len(self.stars)} measurements")

        for m in self.measurements:

            self.controller.stars.unregister_measurement(m)

        if len(self.measurements) == 1:
            if self.old_select:
                self.controller.selections.select(self.old_select)


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
        logging.debug(
            f"COMMAND: Performing aperture photometry on {len(self.measurements)} stars"
        )
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
        logging.debug(f"COMMAND: Undoing photometry on {len(self.measurements)} stars")
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
        self.images = controller.images.all
        self.cmds = []
        for i in self.images:
            measurements = controller.stars.get_measurements_by_image(i)
            self.cmds.append(
                PhotometryMeasurementCommand(
                    measurements, i, self.params, self.controller
                )
            )

    def redo(self):
        logging.debug(
            f"COMMAND: Performing photometry on all measurements in all images"
        )
        for cmd in self.cmds:
            cmd.redo()

    def undo(self):
        logging.debug(f"COMMAND: Undoing photometry on all measurements in all images")
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
        self.images = controller.images.all
        self.cmds = []
        for i in self.images:
            self.cmds.append(DifferentialPhotometryCommand(i, controller))

    def redo(self):
        for cmd in self.cmds:
            cmd.redo()

    def undo(self):
        for cmd in self.cmds:
            cmd.undo()


class PropagateStarSelection(QUndoCommand):
    """Command to propagate measurements from one image to the next"""

    def __init__(self, image: FITSModel, controller: AppController):
        super().__init__("Propagate Star Selection")
        self.controller = controller
        self.image = image
        self.measurements = controller.stars.get_measurements_by_image(image)
        images = controller.images.all
        # All images not ours
        self.others = [i for i in images if i != image]
        self.added = []

    def redo(self):
        logging.debug(f"COMMAND: Propagating stars from image {self.image.uid}")
        for m in self.measurements:
            # Account for drift
            last_m = None
            star = self.controller.stars.get_by_measurement(m)
            for i in self.others:
                if last_m:
                    # If images aren't aligned properly
                    centroid = self.controller.images.find_nearest_centroid(
                        i, last_m.x, last_m.y
                    )
                else:
                    centroid = self.controller.images.find_nearest_centroid(i, m.x, m.y)
                if not centroid:
                    logging.error(
                        f"Unable to find matching centroid at position ({m.x, m.y}) for image {i.uid}"
                    )
                    continue
                new_m = self.controller.stars.create_measurement(
                    centroid["xcentroid"],
                    centroid["ycentroid"],
                    i.observation_time,
                    i.uid,
                    flux=centroid["flux"],
                    mag=centroid["mag"],
                    star=star,
                )
                self.added.append(new_m)
                last_m = new_m

    def undo(self):
        for m in self.added:
            self.controller.stars.unregister_measurement(m)
