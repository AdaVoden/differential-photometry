from __future__ import annotations

from typing import TYPE_CHECKING

from shutterbug.gui.tools.photometry_settings import PhotometryToolSettingsWidget

if TYPE_CHECKING:
    from shutterbug.gui.views.image import ImageViewer
    from shutterbug.core.app_controller import AppController


from shutterbug.gui.operators.operator_parameters import PhotometryParameters
from shutterbug.gui.operators.photometry_operator import PhotometryOperator
from shutterbug.gui.tools.base_tool import BaseTool


class PhotometryTool(BaseTool):
    name = "Photometry"
    icon = None

    params = PhotometryParameters()

    def create_operator(
        self, viewer: ImageViewer, controller: AppController
    ) -> PhotometryOperator:
        return PhotometryOperator(viewer, controller, self.params)

    def create_settings_widget(self) -> PhotometryToolSettingsWidget:
        return PhotometryToolSettingsWidget(self.params)
