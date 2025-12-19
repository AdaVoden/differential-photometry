from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtGui import QMouseEvent, QUndoCommand

from shutterbug.gui.operators.base_settings import BaseSettings

if TYPE_CHECKING:
    from shutterbug.gui.views.image import ImageViewer
    from shutterbug.core.app_controller import AppController

from PySide6.QtCore import QObject, Signal


class BaseOperator(QObject):
    # Notify the UI that things have changed
    finished = Signal(QUndoCommand)
    cancelled = Signal()

    name = "Base Operator"
    listening = True

    def __init__(self, viewer: ImageViewer, controller: AppController):
        super().__init__()
        self.viewer = viewer
        self.controller = controller
        self.active = True

    def create_settings_widget(self) -> BaseSettings | None:
        raise NotImplementedError

    # Called on mouse press
    def start(self, event: QMouseEvent):
        pass

    # Called on mouse move
    def update(self, event: QMouseEvent | None = None):
        pass

    def stop_interaction(self):
        pass

    # Mouse release or enter key
    def confirm(self):
        """Return QUndoCommand or None if no action"""
        cmd = self.build_command()
        self.cleanup_preview()
        self.finished.emit(cmd)

    # Called on escape, RMB or cancel
    def cancel(self):
        self.cleanup_preview()
        self.cancelled.emit()

    # Override me
    def build_command(self) -> QUndoCommand | None:
        return None

    # Override me
    def cleanup_preview(self):
        pass
