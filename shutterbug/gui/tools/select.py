from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtWidgets import QWidget

from shutterbug.gui.operators.select_operator import SelectOperator
from shutterbug.gui.operators.base_operator import BaseOperator

if TYPE_CHECKING:
    from shutterbug.gui.views.image import ImageViewer

from PySide6.QtGui import QMouseEvent
from PySide6.QtCore import Qt
from .base_tool import BaseTool


class SelectTool(BaseTool):
    name = "Select"

    def create_operator(self, viewer: ImageViewer) -> BaseOperator:
        return SelectOperator(viewer)

    def create_settings_widget(self) -> QWidget | None:
        return None
