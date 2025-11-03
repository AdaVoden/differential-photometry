import logging

from shutterbug.gui.controls.labeled_slider import LabeledSlider

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QTabWidget,
)
from PySide6.QtCore import Qt, Slot, Signal
from PySide6.QtGui import QUndoStack


class Settings(QWidget):
    def __init__(self, undo_stack: QUndoStack):
        super().__init__()
        self.setObjectName("settings")

        self._undo_stack = undo_stack

        layout = QVBoxLayout()
        self.setLayout(layout)
        # Remove layout styling
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        # Stacked tabs for that Blender goodness
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        self.tabs.setTabPosition(QTabWidget.TabPosition.West)

        # Different property panels
        self.image_properties = ImagePropertiesPanel(undo_stack)
        self.star_properties = StarPropertiesPanel(undo_stack)
        self.general_properties = GeneralPropertiesPanel(undo_stack)

        self.tabs.addTab(self.general_properties, "Gen")
        self.tabs.addTab(self.image_properties, "Image")
        self.tabs.addTab(self.star_properties, "Star")

        self.show_image_properties()

        logging.debug("Tool settings initialized")

    def show_image_properties(self):
        self.tabs.setCurrentWidget(self.image_properties)

    @Slot()
    def show_star_properties(self, star_data):
        self.star_properties.display_star(star_data)
        self.tabs.setCurrentWidget(self.star_properties)

    def show_general_properties(self):
        self.tabs.setCurrentWidget(self.general_properties)

    def get_state(self):
        return {"image_properties": self.image_properties.get_state()}

    def set_state(self, state):
        self.image_properties.set_state(state["image_properties"])


class ImagePropertiesPanel(QWidget):

    brightness_change_requested = Signal(int)
    contrast_change_requested = Signal(int)

    def __init__(self, undo_stack: QUndoStack):
        super().__init__()

        self._undo_stack = undo_stack

        self.setObjectName("imageProperties")
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Remove layout styling
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

        # Sliders
        self.brightness_slider = LabeledSlider("Brightness", -100, 100, 0)
        self.contrast_slider = LabeledSlider("Contrast", 50, 200, 100)

        # Add to layout
        layout.addWidget(self.brightness_slider)
        layout.addWidget(self.contrast_slider)

        self.brightness_slider.valueChanged.connect(self.brightness_change_requested)
        self.contrast_slider.valueChanged.connect(self.contrast_change_requested)

        logging.debug("Image properties panel initialized")

    @Slot(int)
    def set_brightness(self, value: int):
        self.brightness_slider.setValue(value)

    @Slot(int)
    def set_contrast(self, value: int):
        self.contrast_slider.setValue(value)

    def get_state(self):
        state = {
            "brightness": self.brightness_slider.value(),
            "contrast": self.contrast_slider.value(),
        }
        return state

    def set_state(self, state):
        self.set_brightness(state["brightness"])
        self.set_contrast(state["contrast"])


class StarPropertiesPanel(QWidget):
    def __init__(self, undo_stack: QUndoStack):
        super().__init__()
        self.setObjectName("starProperties")
        layout = QVBoxLayout()
        self.setLayout(layout)

        layout.addWidget(QLabel("Star Information"))

        self.info_labels = {}
        for field in ["Position", "Flux", "Magnitude", "FWHM"]:
            label = QLabel(f"{field}: --")
            self.info_labels[field] = label
            layout.addWidget(label)

        layout.addStretch()

        logging.debug("Star properties panel initialized")

    def display_star(self, star):
        """Update labels with star data"""

        self.info_labels["Position"].setText(f"Position: ({star.x:.1f}, {star.y:.1f})")
        self.info_labels["Flux"].setText(f"Flux: {star.flux:.1f}")

        if star.magnitude:
            self.info_labels["Magnitude"].setText(f"Magnitude: {star.magnitude:.1f}")
        else:
            self.info_labels["Magnitude"].setText("Magnitude: --")


class GeneralPropertiesPanel(QWidget):
    def __init__(self, undo_stack: QUndoStack):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)
        # Add general property controls here
        logging.debug("General properties panel initialized")
