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

        # controls and tooltips
        self.threshold = LabeledSlider(
            "Threshold", 1, 10, self.params.threshold, "float", 3
        )
        self.threshold.setToolTip("Minimum absolute value above background")

        self.sigma = LabeledSlider("Sigma", 1, 10, self.params.sigma, "float", 3)
        self.sigma.setToolTip("Background standard deviation")

        # Add to layout
        layout.addWidget(self.sigma)
        layout.addWidget(self.threshold)

        self.sigma.valueChanged.connect(self._update_threshold)
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
