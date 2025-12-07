from PySide6.QtWidgets import QVBoxLayout
from shutterbug.gui.controls import LabeledSlider, LabeledComboBox
from shutterbug.gui.operators.base_settings import BaseSettings


class PhotometryOperatorSettingsWidget(BaseSettings):

    name = "Photometry"

    def _build_ui(self):
        """Builds UI for Photometry Operator settings"""
        layout = QVBoxLayout(self)
        self.setLayout(layout)
        layout.setSpacing(6)
        layout.setContentsMargins(0, 0, 0, 0)
        self.mode = LabeledComboBox("Mode", ["all", "active"])
        self.aperture = LabeledSlider(
            "Aperture Radius",
            1,
            self.params.annulus_inner_radius - self.params.buffer,
            self.params.aperture_radius,
            "float",
            2,
        )
        self.annulus_inner = LabeledSlider(
            "Inner Annulus Radius",
            self.params.aperture_radius + self.params.buffer,
            self.params.annulus_outer_radius - self.params.buffer,
            self.params.annulus_inner_radius,
            "float",
            2,
        )
        self.annulus_outer = LabeledSlider(
            "Outer Annulus Radius",
            self.params.annulus_inner_radius + self.params.buffer,
            100,  # Arbitrary
            self.params.annulus_outer_radius,
        )

        layout.addWidget(self.mode)
        layout.addWidget(self.aperture)
        layout.addWidget(self.annulus_inner)
        layout.addWidget(self.annulus_outer)


class PhotometryToolSettingsWidget(BaseSettings):

    name = "Photometry"

    def _build_ui(self):
        """Builds UI for Photometry Tool settings"""
        layout = QVBoxLayout(self)
        self.setLayout(layout)
        layout.setSpacing(6)
        layout.setContentsMargins(0, 0, 0, 0)
        self.mode = LabeledComboBox("Mode", ["all", "active"])

        layout.addWidget(self.mode)
