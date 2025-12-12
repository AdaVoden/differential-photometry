from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Slot
from PySide6.QtGui import QMouseEvent, QUndoCommand

from shutterbug.gui.commands.star_commands import (
    PhotometryAllCommand,
    PhotometryMeasurementCommand,
)
from shutterbug.gui.operators.operator_parameters import PhotometryParameters
from shutterbug.gui.tools.photometry_settings import PhotometryOperatorSettingsWidget

if TYPE_CHECKING:
    from shutterbug.gui.views.image import ImageViewer
    from shutterbug.core.app_controller import AppController

from shutterbug.gui.operators.base_operator import BaseOperator
from shutterbug.core.models import MarkerType


class PhotometryOperator(BaseOperator):

    def __init__(
        self,
        viewer: ImageViewer,
        controller: AppController,
        params: PhotometryParameters,
    ):
        super().__init__(viewer, controller)
        self.params = params
        self.listening = True
        self.markers = {}  # (x, y) -> [markers]

        self.params.changed.connect(self._on_params_changed)

    def create_settings_widget(self):
        """Creates settings widget for operator panel"""
        return PhotometryOperatorSettingsWidget(self.params)

    def start(self, event: QMouseEvent):
        """Begins operator function"""
        if self.viewer.current_image is None:
            return
        i_id = self.viewer.current_image.uid
        image_markers = self.controller.markers.markers_from_image(
            self.viewer.current_image
        ).copy()
        inner_colour = self.controller.themes.colours["aperture_inner"]
        outer_colour = self.controller.themes.colours["aperture_outer"]
        for marker in image_markers:
            marker.visible = False
            x = marker.x
            y = marker.y
            aperture = self.controller.markers.create(
                i_id,
                x,
                y,
                MarkerType.APERTURE,
                self.params.aperture_radius,
                inner_colour,
                2,
            )
            annulus_inner = self.controller.markers.create(
                i_id,
                x,
                y,
                MarkerType.ANNULUS_INNER,
                self.params.annulus_inner_radius,
                outer_colour,
                2,
            )
            annulus_outer = self.controller.markers.create(
                i_id,
                x,
                y,
                MarkerType.ANNULUS_OUTER,
                self.params.annulus_outer_radius,
                outer_colour,
                2,
            )
            self.markers[(x, y)] = [aperture, annulus_inner, annulus_outer]

    def update(self, event: QMouseEvent):
        """Updates operator on mouse movement"""
        pass

    def stop_interaction(self):
        """Prevents interaction with operator"""
        self._update_preview()
        self.listening = False

    def build_command(self) -> QUndoCommand | None:
        """Builds photometry measurement command"""
        image = self.viewer.current_image
        if image is None:
            return None
        measurements = self.controller.stars.get_measurements_by_image(image)
        if self.params.images == "single":
            return PhotometryMeasurementCommand(
                measurements, image, self.params, self.controller
            )
        if self.params.images == "all":
            return PhotometryAllCommand(self.params, self.controller)

    def cleanup_preview(self):
        """Returns view to normal"""
        if self.viewer.current_image is None:
            return

        for pos in self.markers:
            for marker in self.markers[pos]:
                self.controller.markers.remove_marker(marker)

        image_markers = self.controller.markers.markers_from_image(
            self.viewer.current_image
        ).copy()
        for marker in image_markers:
            marker.visible = True

    def _update_preview(self):
        """Updates preview"""
        for pos in self.markers:
            # Select
            markers = self.markers[pos]
            aperture = markers[0]
            annulus_inner = markers[1]
            annulus_outer = markers[2]
            # Update
            aperture.radius = self.params.aperture_radius
            annulus_inner.radius = self.params.annulus_inner_radius
            annulus_outer.radius = self.params.annulus_outer_radius

    @Slot()
    def _on_params_changed(self):
        """Handles parameters being changed"""
        if self.active:
            self._update_preview()
