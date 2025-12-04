from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from shutterbug.core.app_controller import AppController

from PySide6.QtCore import QObject


class BaseManager(QObject):
    def __init__(self, controller: AppController, parent=None):
        super().__init__(parent)
        self.controller = controller
