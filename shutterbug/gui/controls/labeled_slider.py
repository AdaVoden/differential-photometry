import logging

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal

from shutterbug.gui.controls.scrubby_slider import ScrubbySlider


class LabeledSlider(QWidget):
    """Reusable labeled slider component"""

    valueChanged = Signal(int)

    def __init__(self, name: str, min: int, max: int, default: int):
        super().__init__()
        layout = QHBoxLayout()
        self.setLayout(layout)
        # Set up margins and spacing
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # Qlabel for display
        self.label = QLabel(name)
        self.label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        layout.addWidget(self.label)

        # Set up scrubby slider from inputs
        self.slider = ScrubbySlider(min, max, default)
        layout.addWidget(self.slider)

        # Attach slider's signal to custom signal
        self.slider.valueChanged.connect(self.valueChanged)

        logging.debug(f"Initialized Labeled Slider: {name}")

    def value(self):
        """Returns value of embedded slider"""
        return self.slider.value()

    def setValue(self, value: int):
        """Sets value of embedded slider"""
        self.slider.setValue(value)
