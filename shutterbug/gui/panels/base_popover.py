from __future__ import annotations

from typing import TYPE_CHECKING

from shutterbug.gui.base_ui_widget import BaseUIWidget

if TYPE_CHECKING:
    from shutterbug.core.app_controller import AppController

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QVBoxLayout


class BasePopOver(BaseUIWidget):
    closed = Signal()

    def __init__(self, controller: AppController, parent=None):
        super().__init__(controller, parent)
        self.setWindowFlags(Qt.WindowType.Widget | Qt.WindowType.FramelessWindowHint)
        # Allow translucent background, don't draw native one
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.setObjectName("popover")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

    def show_at_corner(self):
        pass
