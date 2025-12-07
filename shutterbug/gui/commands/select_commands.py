from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtGui import QUndoCommand

from shutterbug.core.models import StarIdentity

if TYPE_CHECKING:
    from shutterbug.core.app_controller import AppController

import logging


class SelectCommand(QUndoCommand):

    def __init__(self, identity: StarIdentity, controller: AppController):
        super().__init__()
        self.identity = identity
        self.controller = controller
        self.old_identity = self.controller.selections._current

    def redo(self):
        logging.debug(f"COMMAND: Setting active star to {self.identity.id}")
        self.controller.selections.set_selected_object(self.identity)

    def undo(self):
        logging.debug(f"COMMAND: undoing selection of active star {self.identity.id}")
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
