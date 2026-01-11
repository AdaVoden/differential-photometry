from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from shutterbug.core.app_controller import AppController

from .base_command import BaseCommand

from shutterbug.core.models.star_identity import StarIdentity

import logging


class AddGraphCommand(BaseCommand):
    """Command to add a graph to the system"""

    def __init__(self, star: StarIdentity, controller: AppController):
        super().__init__("Add Graph")
        self.star = star
        self.controller = controller
        self.graph = None

    def validate(self):
        """Validates graph creation"""
        for m in self.star.measurements.values():
            if not m.diff_mag or not m.diff_err:
                raise ValueError(
                    "Cannot create graph, star missing differential photometry data"
                )

    def redo(self):
        logging.debug(f"COMMAND: Adding graph to system")
        self.graph = self.controller.graphs.create_from_star(self.star)

    def undo(self):
        logging.debug(f"COMMAND: Undoing graph addition to system")
        if self.graph:
            self.controller.graphs.remove_graph(self.graph)
