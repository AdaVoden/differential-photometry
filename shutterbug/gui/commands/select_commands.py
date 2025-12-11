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
        self.old_identity = self.controller.selections.get(object)

    def redo(self):
        logging.debug(f"COMMAND: Setting active object to {type(self.object).__name__}")
        self.controller.selections.select(self.object)

    def undo(self):
        logging.debug(
            f"COMMAND: undoing selection of object {type(self.object).__name__}"
        )
        self.controller.selections.select(self.old_identity)
