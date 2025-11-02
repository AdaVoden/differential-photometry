import logging

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QTabWidget, QSizePolicy, QSpacerItem
from PySide6.QtCore import Qt, Slot, Signal


class Settings(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("settings")
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
        self.image_properties = ImagePropertiesPanel()
        self.star_properties = StarPropertiesPanel()
        self.general_properties = GeneralPropertiesPanel()

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

class SliderSettingsWidget(QWidget):

    valueChanged = Signal(int)
    
    def __init__(self, name: str, min: int, max: int, default: int):
        super().__init__()
        layout = QHBoxLayout()
        # Set up margins and spacing
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        # Set up alignment and size policy
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        self.setLayout(layout)

        self.label = QLabel(name)
        self.label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.label)
        # Spacer for central alignment
        self.spacer = QSpacerItem(10, 5, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
        layout.addItem(self.spacer)

        # Set up slider from inputs
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(min, max)
        self.slider.setValue(default)
        self.slider.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        layout.addWidget(self.slider)

        # Attach slider's signal to custom signal
        self.slider.valueChanged.connect(self.valueChanged)

    def value(self):
        """Returns value of embedded slider"""
        return self.slider.value()
    
    def setValue(self, value: int):
        """Sets value of embedded slider"""
        self.slider.setValue(value)
        

class ImagePropertiesPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("imageProperties")
        layout = QVBoxLayout()
        self.setLayout(layout)
        # Remove layout styling
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Brightness slider
        self.brightness_slider = SliderSettingsWidget("Brightness", -100, 100, 0)
        layout.addWidget(self.brightness_slider)

        # Contrast slider
        self.contrast_slider = SliderSettingsWidget("Contrast", 50, 200, 100)
        layout.addWidget(self.contrast_slider)

        # Take up all extra space
        layout.addStretch()

        logging.debug("Image properties panel initialized")

    def set_brightness(self, value: int):
        if value < -100:
            raise ValueError("Brightness set too low")
        if value > 100:
            raise ValueError("Brightness set too high")
        self.brightness_slider.slider.setValue(value)

    def set_contrast(self, value):
        if value < 50:
            raise ValueError("Contrast set too low")
        if value > 200:
            raise ValueError("Contrast set too high")
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
    def __init__(self):
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

        # TODO FWHM from star


class GeneralPropertiesPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)
        # Add general property controls here
        logging.debug("General properties panel initialized")
