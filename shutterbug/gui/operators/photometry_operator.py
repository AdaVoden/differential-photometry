from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Slot
from PySide6.QtGui import QMouseEvent

from shutterbug.gui.operators.operator_parameters import PhotometryParameters
from shutterbug.gui.tools.photometry_settings import PhotometryOperatorSettingsWidget

if TYPE_CHECKING:
    from shutterbug.gui.views.image import ImageViewer
    from shutterbug.core.app_controller import AppController

from shutterbug.gui.operators.base_operator import BaseOperator


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
        self.markers = {}
        self.photometry_markers = {}

        self.params.changed.connect(self._on_params_changed)

    def create_settings_widget(self):
        return PhotometryOperatorSettingsWidget(self.params)

    def start(self, event: QMouseEvent):
        self.markers = self.viewer.markers.copy()
        self._update_preview()

    def update(self, event: QMouseEvent):
        pass

    def stop_interaction(self):
        self._update_preview()
        self.listening = False

    def build_command(self) -> QUndoCommand | None:
        pass

    def cleanup_preview(self):
        marker_positions = self.viewer.markers.copy().keys()
        for x, y in marker_positions:
            self.viewer.remove_star_marker(x, y)
            self.viewer.add_star_marker(x, y)

    def _update_preview(self):
        marker_positions = self.viewer.markers.copy().keys()
        for x, y in marker_positions:
            self.viewer.remove_star_marker(x, y)
            self.viewer.add_star_marker(x, y, self.params.aperture_radius, "magenta")
            self.viewer.add_star_marker(x, y, self.params.annulus_inner_radius, "red")
            self.viewer.add_star_marker(x, y, self.params.annulus_outer_radius, "red")

    @Slot()
    def _on_params_changed(self):
        if self.active:
            self._update_preview()
