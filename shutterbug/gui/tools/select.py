from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from shutterbug.gui.views.image import ImageViewer

from PySide6.QtGui import QMouseEvent
from PySide6.QtCore import Qt
from .base_tool import Tool


class SelectTool(Tool):

    def __init__(self):
        super().__init__()
        self._name = "Select"

    def mouse_press(self, viewer: ImageViewer, event: QMouseEvent):
        # Alt + Click, remove a star
        if event.modifiers() == Qt.KeyboardModifier.AltModifier:
            if event.button() == Qt.MouseButton.LeftButton:
                viewer.deselect_star(event.pos())
            return

        if event.button() == Qt.MouseButton.LeftButton:
            viewer.select_star(event.pos())
            return
