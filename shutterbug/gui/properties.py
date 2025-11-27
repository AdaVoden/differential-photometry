from __future__ import annotations

from typing import TYPE_CHECKING

from shutterbug.gui.operators.base_operator import BaseOperator

if TYPE_CHECKING:
    from shutterbug.gui.main_window import MainWindow

import logging

from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QUndoStack
from PySide6.QtWidgets import QLabel, QTabWidget, QVBoxLayout, QWidget
from shutterbug.core.managers import ImageManager
from shutterbug.core.models import FITSModel
from shutterbug.gui.commands.image_commands import (
    SetBrightnessCommand,
    SetContrastCommand,
)
from shutterbug.gui.controls.labeled_slider import LabeledSlider
from shutterbug.gui.tools.base_tool import BaseTool
from shutterbug.gui.panels.collapsible_section import CollapsibleSection


class Properties(QWidget):
    def __init__(self, undo_stack: QUndoStack, main_window: MainWindow):
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
        self.tool_properties = ToolPropertiesPanel()
        self.image_properties = ImagePropertiesPanel(undo_stack)
        self.star_properties = StarPropertiesPanel(undo_stack)
        self.general_properties = GeneralPropertiesPanel(undo_stack)

        self.tabs.addTab(self.tool_properties, "Tool")
        self.tabs.addTab(self.general_properties, "Gen")
        self.tabs.addTab(self.image_properties, "Image")
        self.tabs.addTab(self.star_properties, "Star")

        self.show_image_properties()

        # Main Window signals
        main_window.active_tool_changed.connect(self._on_active_tool_change)
        main_window.tool_settings_changed.connect(self._on_settings_change)

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

    @Slot(BaseTool)
    def _on_active_tool_change(self, tool: BaseTool):
        self.tool_properties.set_tool_name(tool)

    @Slot(QWidget)
    def _on_settings_change(self, settings: QWidget):
        self.tool_properties.set_panel(settings)


class ImagePropertiesPanel(QWidget):

    def __init__(self, undo_stack: QUndoStack):
        super().__init__()

        self._undo_stack = undo_stack

        self.image_manager = ImageManager()
        self.current_image = self.image_manager.active_image

        self.setObjectName("imageProperties")
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        # Remove layout styling
        layout.setContentsMargins(16, 8, 8, 8)
        layout.setSpacing(5)

        # Sliders
        self.brightness_slider = LabeledSlider("Brightness", -100, 100, 0, "int")
        self.contrast_slider = LabeledSlider("Contrast", 0, 2, 1, "float", 3)

        # Panel
        self.settings_panel = CollapsibleSection(
            "Image Settings", [self.brightness_slider, self.contrast_slider], self
        )

        layout.addWidget(self.settings_panel)

        # Signals to slots
        self.brightness_slider.valueChanged.connect(self._on_brightness_changed)
        self.contrast_slider.valueChanged.connect(self._on_contrast_changed)

        self.image_manager.active_image_changed.connect(self._on_image_changed)

        logging.debug("Image properties panel initialized")

    @Slot(FITSModel)
    def _on_image_changed(self, image: FITSModel):
        """Handles image changing in image manager"""
        if self.current_image:
            # There's a current image remove all previous subscriptions
            self.current_image.updated.disconnect(self.set_brightness)
            self.current_image.updated.disconnect(self.set_contrast)

        self.current_image = image

        if image:
            # Add new subscriptions and set the slider values
            image.updated.connect(self.set_brightness)
            image.updated.connect(self.set_contrast)
            self.set_brightness(image)
            self.set_contrast(image)

    @Slot(int)
    def _on_brightness_changed(self, value: int):
        if self.current_image:
            self._undo_stack.push(SetBrightnessCommand(value, self.current_image))

    @Slot(int)
    def _on_contrast_changed(self, value: int):
        if self.current_image:
            self._undo_stack.push(SetContrastCommand(value, self.current_image))

    @Slot(FITSModel)
    def set_brightness(self, image: FITSModel):
        value = image.brightness
        self.brightness_slider.setValue(value)

    @Slot(FITSModel)
    def set_contrast(self, image: FITSModel):
        value = image.contrast
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


class ToolPropertiesPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        layout.setContentsMargins(16, 8, 8, 8)
        layout.setSpacing(5)
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        self.tool_name = None
        self.tool_icon = None

        logging.debug("Tool properties panel initialized")

    @Slot(BaseTool)
    def set_tool_name(self, tool: BaseTool):
        self.tool_name = tool.name
        self.tool_icon = tool.icon

    @Slot(QWidget)
    def set_panel(self, settings_widget: QWidget):
        """Sets tool widgets"""
        # Remove old stuff
        layout = self.layout()
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                if w := item.widget():
                    w.deleteLater()

            # Add new stuff
            label = QLabel(self.tool_name)
            layout.addWidget(label)
            if settings_widget is not None:
                section = CollapsibleSection("Options", [settings_widget], self)
                layout.addWidget(section)
