from PySide6.QtCore import Slot
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
            "Aperture",
            1,
            100,
            self.params.aperture_radius,
            self.params.number_type,
            self.params.decimal_places,
        )
        self.annulus_inner = LabeledSlider(
            "Inner Annulus",
            1,
            100,
            self.params.annulus_inner_radius,
            self.params.number_type,
            self.params.decimal_places,
        )
        self.annulus_outer = LabeledSlider(
            "Outer Annulus",
            1,
            100,  # Arbitrary
            self.params.annulus_outer_radius,
            self.params.number_type,
            self.params.decimal_places,
        )

        self.aperture.valueChanged.connect(self._update_aperture)
        self.annulus_inner.valueChanged.connect(self._update_annulus_inner)
        self.annulus_outer.valueChanged.connect(self._update_annulus_outer)

        layout.addWidget(self.mode)
        layout.addWidget(self.aperture)
        layout.addWidget(self.annulus_inner)
        layout.addWidget(self.annulus_outer)

    @Slot(float)
    def _update_aperture(self, value: float):
        """Updates parameter Aperture Radius in params"""
        self.params.aperture_radius = value
        if value >= self.annulus_inner.value:
            # Make annulus bigger to accommodate aperture
            self.annulus_inner.set_value(value + self.params.buffer)
        self.params.changed.emit()

    @Slot(float)
    def _update_annulus_inner(self, value: float):
        """Updates parameter Annulus Inner Radius in params"""
        self.params.annulus_inner_radius = value
        if value <= self.aperture.value:
            # Make aperture smaller to accommodate annulus
            self.aperture.set_value(value - self.params.buffer)
        if value >= self.annulus_outer.value:
            # Make outer annulus larger to accommodate annulus
            self.annulus_outer.set_value(value + self.params.buffer)
        self.params.changed.emit()

    @Slot(float)
    def _update_annulus_outer(self, value: float):
        """Updates parameter Annulus Outer Radius in params"""
        self.params.annulus_outer_radius = value
        if value <= self.annulus_inner.value:
            # Make inner annulus smaller to accommodate outer
            self.annulus_inner.set_value(value - self.params.buffer)
        self.params.changed.emit()


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
