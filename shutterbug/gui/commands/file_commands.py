from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from shutterbug.core.app_controller import AppController

from .base_command import BaseCommand
from shutterbug.core.models import FITSModel

from pathlib import Path

from typing import List

import logging


class LoadImagesCommand(BaseCommand):
    """Loads images into application"""

    def __init__(self, image_paths: List[str], controller: AppController):
        super().__init__("Load Images")
        self.image_paths = [Path(f) for f in image_paths]
        self.controller = controller
        self.images = []

    def validate(self):
        pass

    def redo(self) -> None:
        logging.debug(
            f"COMMAND: Load images command activated for {len(self.image_paths)} images"
        )
        for path in self.image_paths:
            image = self.controller.files.load(path)
            if image:
                self.controller.images.add_image(image)
                self.images.append(image)

    def undo(self) -> None:
        logging.debug(f"COMMAND: Undoing image load of {len(self.image_paths)} images")
        for image in self.images:
            self.controller.images.remove_image(image)

        self.images.clear()


class SelectFileCommand(BaseCommand):
    """Selects file in outliner and viewer"""

    def __init__(self, selected_image: FITSModel, controller: AppController):
        super().__init__("Select File")
        self.selected_image = selected_image
        self.controller = controller
        self.last_selection = None

    def validate(self):
        pass

    def redo(self) -> None:
        logging.debug(
            f"COMMAND: Setting active image to: {self.selected_image.filename}"
        )
        self.last_selection = self.controller.selections._current
        self.controller.selections.select(self.selected_image)

    def undo(self) -> None:
        logging.debug(
            f"COMMAND: undoing setting active image to: {self.selected_image.filename}"
        )

        self.controller.selections.select(self.last_selection)
