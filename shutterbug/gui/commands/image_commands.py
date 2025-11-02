from PySide6.QtGui import QUndoCommand

from shutterbug.gui.tool_settings import ImagePropertiesPanel


class SetBrightnessCommand(QUndoCommand):
    def __init__(
        self, image_panel: ImagePropertiesPanel, old_value: int, new_value: int
    ):
        super().__init__("Set Brightness")
        self.image_panel = image_panel
        self.old_value = old_value
        self.new_value = new_value

    def redo(self) -> None:
        self.image_panel.set_brightness(self.new_value)

    def undo(self) -> None:
        self.image_panel.set_brightness(self.old_value)


class SetContrastCommand(QUndoCommand):
    def __init__(
        self, image_panel: ImagePropertiesPanel, old_value: int, new_value: int
    ):
        super().__init__("Set Contrast")
        self.image_panel = image_panel
        self.old_value = old_value
        self.new_value = new_value

    def redo(self) -> None:
        self.image_panel.set_contrast(self.new_value)

    def undo(self) -> None:
        self.image_panel.set_contrast(self.old_value)
