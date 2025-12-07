from __future__ import annotations

from typing import TYPE_CHECKING

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

    def create_settings_widget(self):
        return PhotometryOperatorSettingsWidget(self.params)

    def start(self, event: QMouseEvent):
        pass

    def update(self, event: QMouseEvent):
        pass

    def stop_interaction(self):
        pass

    def build_command(self) -> QUndoCommand | None:
        pass

    def cleanup_preview(self):
        pass
