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
        self._subscription_ids = []
        # Assuming direct control of theme
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setAutoFillBackground(True)

    def subscribe(self, pattern: str, callback):
        """Helper that tracks subscriptions for cleanup"""
        sub_id = self.controller.on(pattern, callback)
        self._subscription_ids.append(sub_id)

    def _cleanup(self):
        """Unsubscribe from everything"""
        for sub_id in self._subscription_ids:
            self.controller.off(sub_id)
        self._subscription_ids.clear()

    def on_activated(self):
        """Handles activation of UI Widget"""
        pass

    def on_deactivated(self):
        """Handes deactivation of UI Widget"""
        self._cleanup()
