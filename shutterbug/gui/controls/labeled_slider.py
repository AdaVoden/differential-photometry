import logging

from PySide6.QtCore import Signal

from .labeled_widget import LabeledWidget
from .scrubby_slider import ScrubbySlider


class LabeledSlider(LabeledWidget):
    """Reusable labeled slider component"""

    valueChanged = Signal(float)

    def __init__(
        self,
        label: str,
        min: float,
        max: float,
        default: float,
        number_type: str = "int",
        decimal_places: int = 3,
    ):
        super().__init__(label)
        # Set up scrubby slider from inputs
        self.slider = ScrubbySlider(min, max, default, number_type, decimal_places)
        layout = self.layout()
        if layout is not None:
            layout.addWidget(self.slider)

        # Attach slider's signal to custom signal
        self.slider.valueChanged.connect(self.valueChanged)

        logging.debug(f"Initialized Labeled Slider: {label}")

    @property
    def value(self):
        """Returns value of embedded slider"""
        return self.slider.value()

    def set_value(self, value: float):
        """Sets value of embedded slider"""
        self.slider.setValue(value)
