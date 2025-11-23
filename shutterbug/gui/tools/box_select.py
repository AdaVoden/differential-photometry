from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtGui import QMouseEvent

if TYPE_CHECKING:
    from shutterbug.gui.views.image import ImageViewer

from shutterbug.gui.tools.base_tool import Tool


class BoxSelectTool(Tool):

    def __init__(self):
        super().__init__()
        self._name = "BoxSelect"

    def mouse_press(self, viewer: ImageViewer, event: QMouseEvent):
        pass

    def mouse_move(self, viewer: ImageViewer, event: QMouseEvent):
        pass

    def mouse_release(self, viewer: ImageViewer, event: QMouseEvent):
        pass
