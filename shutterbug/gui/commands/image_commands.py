from PySide6.QtGui import QUndoCommand

from shutterbug.gui.image_data import FITSImage


class SetBrightnessCommand(QUndoCommand):

    def __init__(self, new_value: int, image: FITSImage):
        super().__init__("Set Brightness")
        self.new_value = new_value
        self.image = image

        self.old_value = image.brightness

    def redo(self) -> None:
        self.image.brightness = self.new_value

    def undo(self) -> None:
        self.image.brightness = self.old_value


class SetContrastCommand(QUndoCommand):
    def __init__(self, new_value: int, image: FITSImage):
        super().__init__("Set Contrast")
        self.new_value = new_value
        self.image = image

        self.old_value = image.contrast

    def redo(self) -> None:
        self.image.contrast = self.new_value

    def undo(self) -> None:
        self.image.contrast = self.old_value
