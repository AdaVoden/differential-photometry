from shutterbug.core.app_controller import AppController
from shutterbug.core.events.change_event import Event
import logging

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QLabel, QTabWidget, QVBoxLayout, QWidget
from shutterbug.gui.commands.image_commands import (
    SetBrightnessCommand,
    SetContrastCommand,
)
from shutterbug.gui.controls import LabeledSlider, LabeledComboBox
from shutterbug.gui.tools.base_tool import BaseTool
from shutterbug.gui.panels.collapsible_section import CollapsibleSection
from shutterbug.core.LUTs.registry import STRETCH_REGISTRY


class Properties(QWidget):
    def __init__(self, controller: AppController):
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
        self.tool_properties = ToolPropertiesPanel(controller)
        self.image_properties = ImagePropertiesPanel(controller)
        self.star_properties = StarPropertiesPanel(controller)
        self.general_properties = GeneralPropertiesPanel(controller)

        self.tabs.addTab(self.tool_properties, "Tool")
        self.tabs.addTab(self.general_properties, "Gen")
        self.tabs.addTab(self.image_properties, "Image")
        self.tabs.addTab(self.star_properties, "Star")

        self.show_image_properties()

        # Main Window signals
        controller.active_tool_changed.connect(self._on_active_tool_change)

        logging.debug("Tool settings initialized")

    def show_image_properties(self):
        self.tabs.setCurrentWidget(self.image_properties)

    @Slot()
    def show_star_properties(self, star_data):
        self.star_properties.display_star(star_data)
        self.tabs.setCurrentWidget(self.star_properties)

    def show_general_properties(self):
        self.tabs.setCurrentWidget(self.general_properties)

    @Slot(BaseTool)
    def _on_active_tool_change(self, tool: BaseTool):
        self.tool_properties.set_panel(tool)


class ImagePropertiesPanel(QWidget):

    def __init__(self, controller: AppController):
        super().__init__()

        self._undo_stack = controller._undo_stack

        self.current_image = None

        self.setObjectName("imageProperties")
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        # Remove layout styling
        layout.setContentsMargins(16, 8, 8, 8)
        layout.setSpacing(5)

        # Stretch combo box
        self.stretches = LabeledComboBox("Stretch", list(STRETCH_REGISTRY.keys()))

        # Sliders
        self.brightness_slider = LabeledSlider("Brightness", -0.5, 0.5, 0, "float")
        self.contrast_slider = LabeledSlider("Contrast", 0.5, 1.5, 1, "float", 3)

        # Panel
        self.settings_panel = CollapsibleSection(
            "Image Settings",
            [self.stretches, self.brightness_slider, self.contrast_slider],
            self,
        )

        layout.addWidget(self.settings_panel)

        # Signals to slots
        self.brightness_slider.valueChanged.connect(self._on_brightness_changed)
        self.contrast_slider.valueChanged.connect(self._on_contrast_changed)

        controller.on("image.selected", self._on_image_selected)
        controller.on(
            "image.updated.brightness",
            lambda evt: self.brightness_slider.set_value(evt.data),
        )
        controller.on(
            "image.updated.contrast",
            lambda evt: self.contrast_slider.set_value(evt.data),
        )
        controller.on(
            "image.updated.stretch_type", lambda evt: self.stretches.set_text(evt.data)
        )

        logging.debug("Image properties panel initialized")

    @Slot(Event)
    def _on_image_selected(self, event: Event):
        """Handles image changing in image manager"""
        image = event.data

        if image:
            # Add new subscriptions and set the slider values
            self.brightness_slider.set_value(image.brightness)
            self.contrast_slider.set_value(image.contrast)
            self.stretches.set_text(image.stretch_type)

    @Slot(int)
    def _on_brightness_changed(self, value: int):
        if self.current_image:
            self._undo_stack.push(SetBrightnessCommand(value, self.current_image))

    @Slot(int)
    def _on_contrast_changed(self, value: int):
        if self.current_image:
            self._undo_stack.push(SetContrastCommand(value, self.current_image))


class StarPropertiesPanel(QWidget):
    def __init__(self, controller: AppController):
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
    def __init__(self, controller: AppController):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)
        # Add general property controls here
        logging.debug("General properties panel initialized")


class ToolPropertiesPanel(QWidget):
    def __init__(self, controller: AppController):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        layout.setContentsMargins(16, 8, 8, 8)
        layout.setSpacing(5)
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        logging.debug("Tool properties panel initialized")

    @Slot(BaseTool)
    def set_panel(self, tool: BaseTool):
        """Sets tool widgets"""
        # Remove old stuff
        layout = self.layout()
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                if w := item.widget():
                    w.deleteLater()

            # Add new stuff
            label = QLabel(tool.name)
            layout.addWidget(label)
            settings = tool.create_settings_widget()
            if settings is not None:
                section = CollapsibleSection("Options", [settings], self)
                layout.addWidget(section)
