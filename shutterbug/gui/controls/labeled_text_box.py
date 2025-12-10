import logging
from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QLineEdit
from .labeled_widget import LabeledWidget


class LabeledTextBox(LabeledWidget):
    """Reusable text box widget"""

    editing_finished = Signal(str)

    def __init__(self, label: str):
        super().__init__(label)

        self.edit = QLineEdit()
        layout = self.layout()
        if layout is not None:
            layout.addWidget(self.edit)

        self.edit.editingFinished.connect(self._on_editing_finished)

        logging.debug(f"Initialized Labeled Edit Box: {label}")

    @property
    def text(self):
        """Returns the current text in the box"""
        return self.edit.text()

    def set_text(self, text: str):
        """Sets the box text to input"""
        self.edit.setText(text)

    @Slot()
    def _on_editing_finished(self):
        """Handles text box finishing editing"""
        self.editing_finished.emit(self.text)
