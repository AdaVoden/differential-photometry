from PySide6.QtCore import Slot
from PySide6.QtWidgets import QVBoxLayout, QWidget
from shutterbug.gui.controls.labeled_slider import LabeledSlider
from shutterbug.gui.operators.operator_parameters import BoxSelectParameters


class BoxSelectSettingsWidget(QWidget):
    def __init__(self, params: BoxSelectParameters):
        super().__init__()
        self.params = params
        self._build_ui()

    def _build_ui(self):
        """Builds UI for settings"""
        layout = QVBoxLayout(self)
        self.threshold = LabeledSlider(
            "Threshold", 0, 5, self.params.threshold, "float", 3
        )
        layout.addWidget(self.threshold)

        self.threshold.valueChanged.connect(self._update_threshold)

    @Slot(float)
    def _update_threshold(self, value: float):
        """Updates parameter Threshold in params"""
        self.params.threshold = value
        self.params.changed.emit()
