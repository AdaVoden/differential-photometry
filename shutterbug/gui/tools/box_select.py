from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from shutterbug.gui.views.image import ImageViewer

from shutterbug.gui.operators.box_select_operator import BoxSelectOperator
from shutterbug.gui.tools.base_tool import BaseTool
from shutterbug.gui.controls import LabeledSlider


class BoxSelectTool(BaseTool):
    name = "Box Select"

    def create_operator(self, viewer: ImageViewer):
        return BoxSelectOperator(viewer)

    def create_settings_widget(self):

        threshold = LabeledSlider("Threshold", 0, 5, 3, "float", 3)
        threshold.valueChanged.connect(lambda v: setattr(self, "threshold", v))

        return threshold
