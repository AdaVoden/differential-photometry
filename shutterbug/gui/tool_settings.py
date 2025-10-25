import logging
from PySide6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget, QLabel, QSlider
from PySide6.QtCore import Qt


class Settings(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Stacked tabs for that Blender goodness
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

        # Different property panels
        self.image_properties = ImagePropertiesPanel()
        self.star_properties = StarPropertiesPanel()
        self.general_properties = GeneralPropertiesPanel()

        self.stack.addWidget(self.image_properties)
        self.stack.addWidget(self.star_properties)
        self.stack.addWidget(self.general_properties)

        logging.debug("Tool settings initialized")

    def show_image_properties(self):
        self.stack.setCurrentWidget(self.image_properties)

    def show_star_properties(self):
        self.stack.setCurrentWidget(self.star_properties)

    def show_general_properties(self):
        self.stack.setCurrentWidget(self.general_properties)


class ImagePropertiesPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Brightness slider
        layout.addWidget(QLabel("Brightness"))
        self.brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setRange(-100, 100)
        self.brightness_slider.setValue(0)
        layout.addWidget(self.brightness_slider)

        # Contrast slider
        layout.addWidget(QLabel("Contrast"))
        self.contrast_slider = QSlider(Qt.Orientation.Horizontal)
        self.contrast_slider.setRange(50, 200)
        self.contrast_slider.setValue(100)
        layout.addWidget(self.contrast_slider)

        logging.debug("Image properties panel initialized")


class StarPropertiesPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)
        # Add star property controls here
        logging.debug("Star properties panel initialized")


class GeneralPropertiesPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)
        # Add general property controls here
        logging.debug("General properties panel initialized")
