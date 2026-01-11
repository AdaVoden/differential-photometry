from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from shutterbug.core.app_controller import AppController

from .base_command import BaseCommand

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
        for p in self.image_paths:
            if not p.is_file():
                raise ValueError(f"File {p.name} not found or is a directory")

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
