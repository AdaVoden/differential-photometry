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
        self._drag_start = None

    def mouse_press(self, viewer: ImageViewer, event: QMouseEvent):
        self._drag_start = event.pos()

    def mouse_move(self, viewer: ImageViewer, event: QMouseEvent):
        if self._drag_start:
            end = event.pos()
            viewer.update_selection_rect(self._drag_start, end)

    def mouse_release(self, viewer: ImageViewer, event: QMouseEvent):
        if self._drag_start:
            end = event.pos()
            viewer.apply_box_selection(self._drag_start, end)
        self._drag_start = None
