from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from shutterbug.core.app_controller import AppController

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt


class BaseUIWidget(QWidget):
    """Base widget with theme support"""

    def __init__(self, controller: AppController, parent=None):
        super().__init__(parent)
        self.controller = controller

        # Assuming direct control of theme
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setAutoFillBackground(True)
