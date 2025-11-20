import logging
from PySide6.QtGui import QUndoCommand

from shutterbug.core.models import FITSModel


class SetBrightnessCommand(QUndoCommand):

    def __init__(self, new_value: int, image: FITSModel):
        super().__init__("Set Brightness")
        self.new_value = new_value
        self.image = image

        self.old_value = image.brightness

    def redo(self) -> None:
        logging.debug(f"COMMAND: Setting brightness to: {self.new_value}")
        self.image.brightness = self.new_value

    def undo(self) -> None:
        logging.debug(
            f"COMMAND: Undoing setting contrast, setting to old value: {self.old_value}"
        )

        self.image.brightness = self.old_value


class SetContrastCommand(QUndoCommand):
    def __init__(self, new_value: int, image: FITSModel):
        super().__init__("Set Contrast")
        self.new_value = new_value
        self.image = image

        self.old_value = image.contrast

    def redo(self) -> None:
        logging.debug(f"COMMAND: Setting contrast to: {self.new_value}")
        self.image.contrast = self.new_value

    def undo(self) -> None:
        logging.debug(
            f"COMMAND: Undoing setting contrast, setting to old value: {self.old_value}"
        )
        self.image.contrast = self.old_value
