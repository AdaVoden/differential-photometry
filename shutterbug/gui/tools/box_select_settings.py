from PySide6.QtCore import Slot
from PySide6.QtWidgets import QVBoxLayout
from shutterbug.gui.controls.labeled_slider import LabeledSlider
from shutterbug.gui.operators.base_settings import BaseSettings


class BoxSelectOperatorSettingsWidget(BaseSettings):

    name = "Box Select"

    def _build_ui(self):
        """Builds UI for settings"""
        layout = QVBoxLayout(self)
        self.setLayout(layout)
        layout.setSpacing(6)
        layout.setContentsMargins(0, 0, 0, 0)
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


class BoxSelectToolSettingsWidget(BaseSettings):

    name = "Box Select"

    def _build_ui(self):
        return None
