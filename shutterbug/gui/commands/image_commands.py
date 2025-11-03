from __future__ import annotations
from typing import TYPE_CHECKING
# Prevent circular import due to type checking
if TYPE_CHECKING:
    from shutterbug.gui.tool_settings import ImagePropertiesPanel
    from shutterbug.gui.viewer import Viewer

from PySide6.QtGui import QUndoCommand

class SetBrightnessCommand(QUndoCommand):
    
    def __init__(
        self, image_panel: ImagePropertiesPanel, viewer: Viewer, new_value: int
    ):
        super().__init__("Set Brightness")
        self.image_panel = image_panel
        self.viewer = viewer
        self.old_value = image_panel.brightness_slider.value()
        self.new_value = new_value

    def redo(self) -> None:
        self.image_panel.set_brightness(self.new_value)
        self.viewer.set_brightness(self.new_value)

    def undo(self) -> None:
        self.image_panel.set_brightness(self.old_value)
        self.viewer.set_brightness(self.old_value)


class SetContrastCommand(QUndoCommand):
    def __init__(
        self, image_panel: ImagePropertiesPanel, viewer: Viewer, new_value: int
    ):
        super().__init__("Set Contrast")
        self.image_panel = image_panel
        self.viewer = viewer
        self.old_value = image_panel.contrast_slider.value()
        self.new_value = new_value

    def redo(self) -> None:
        self.image_panel.set_contrast(self.new_value)
        self.viewer.set_contrast(self.new_value)

    def undo(self) -> None:
        self.image_panel.set_contrast(self.old_value)
        self.viewer.set_contrast(self.old_value)
