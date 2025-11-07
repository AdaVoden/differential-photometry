import logging

from shutterbug.gui.controls.labeled_slider import LabeledSlider
from shutterbug.gui.image_manager import ImageManager
from shutterbug.gui.image_data import FITSImage
from shutterbug.gui.commands.image_commands import (
    SetBrightnessCommand,
    SetContrastCommand,
)

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QTabWidget,
)
from PySide6.QtCore import Qt, Slot
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

    def __init__(self, undo_stack: QUndoStack):
        super().__init__()

        self._undo_stack = undo_stack

        self.image_manager = ImageManager()
        self.current_image = self.image_manager.active_image

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

        # Signals to slots
        self.brightness_slider.valueChanged.connect(self._on_brightness_changed)
        self.contrast_slider.valueChanged.connect(self._on_contrast_changed)

        self.image_manager.active_image_changed.connect(self._on_image_changed)

        logging.debug("Image properties panel initialized")

    @Slot(FITSImage)
    def _on_image_changed(self, image: FITSImage):
        """Handles image changing in image manager"""
        if self.current_image:
            # There's a current image remove all previous subscriptions
            self.current_image.brightness_changed.disconnect(self.set_brightness)
            self.current_image.contrast_changed.disconnect(self.set_contrast)

        self.current_image = image

        if image:
            # Add new subscriptions and set the slider values
            image.brightness_changed.connect(self.set_brightness)
            image.contrast_changed.connect(self.set_contrast)
            self.set_brightness(image.brightness)
            self.set_contrast(image.contrast)

    @Slot(int)
    def _on_brightness_changed(self, value: int):
        if self.current_image:
            self._undo_stack.push(SetBrightnessCommand(value, self.current_image))

    @Slot(int)
    def _on_contrast_changed(self, value: int):
        if self.current_image:
            self._undo_stack.push(SetContrastCommand(value, self.current_image))

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
