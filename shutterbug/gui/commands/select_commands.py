from __future__ import annotations

from typing import TYPE_CHECKING, Any

from PySide6.QtGui import QUndoCommand

if TYPE_CHECKING:
    from shutterbug.core.app_controller import AppController

import logging


class SelectCommand(QUndoCommand):

    def __init__(self, object: Any, controller: AppController):
        super().__init__()
        self.object = object
        self.controller = controller
        self.old_identity = self.controller.selections._current

    def redo(self):
        logging.debug(f"COMMAND: Setting active object to {type(self.object).__name__}")
        self.controller.selections.set_selected_object(self.object)

    def undo(self):
        logging.debug(
            f"COMMAND: undoing selection of object {type(self.object).__name__}"
        )
        self.controller.selections.set_selected_object(self.old_identity)


class DeselectCommand(QUndoCommand):

    def __init__(self, controller: AppController):
        super().__init__()
        self.controller = controller
        self.old_identity = self.controller.selections._current

    def redo(self):
        logging.debug(f"COMMAND: removing active star selection")
        self.controller.selections.set_selected_object(None)

    def undo(self):
        logging.debug(f"COMMAND: undoing removal of active star")
        self.controller.selections.set_selected_object(self.old_identity)
