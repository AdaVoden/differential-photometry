from __future__ import annotations

from typing import TYPE_CHECKING

from shutterbug.gui.operators.operator_parameters import BoxSelectParameters
from shutterbug.gui.tools.box_select_settings import BoxSelectToolSettingsWidget

if TYPE_CHECKING:
    from shutterbug.gui.views.image import ImageViewer

from shutterbug.gui.operators.box_select_operator import BoxSelectOperator
from shutterbug.gui.tools.base_tool import BaseTool


class BoxSelectTool(BaseTool):
    name = "Box Select"

    params = BoxSelectParameters()

    def create_operator(self, viewer: ImageViewer):
        return BoxSelectOperator(viewer, self.params)

    def create_settings_widget(self):
        return BoxSelectToolSettingsWidget(self.params)
