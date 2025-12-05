from typing import List
from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QComboBox
from .labeled_widget import LabeledWidget

import logging


class LabeledComboBox(LabeledWidget):
    """Reusable combo box widget"""

    activated = Signal(str)

    def __init__(self, label: str, items: List[str]):
        super().__init__(label)

        self.combo = QComboBox()
        self.combo.setEditable(False)
        layout = self.layout()
        if layout is not None:
            layout.addWidget(self.combo)

        self.combo.addItems(items)

        self.combo.activated.connect(self._on_activated)
        logging.debug(f"Initialized Labeled Combo Box: {label}")

    @Slot(int)
    def _on_activated(self, index: int):
        """Handles index return on user activation"""
        text = self.combo.itemText(index)
        if text is not None:
            self.activated.emit(text)

    def text(self):
        """Returns current value of combo box"""
        return self.combo.currentText()

    def set_text(self, text: str):
        idx = self.combo.findText(text)
        if idx:
            self.combo.setCurrentIndex(idx)
