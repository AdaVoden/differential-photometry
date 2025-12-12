from shutterbug.core.app_controller import AppController
from shutterbug.core.events.change_event import Event
import logging

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QLabel, QTabWidget, QVBoxLayout, QWidget
from shutterbug.gui.commands import SetGraphValueCommand, SetImageValueCommand
from shutterbug.gui.controls import LabeledSlider, LabeledComboBox
from shutterbug.gui.controls.labeled_text_box import LabeledTextBox
from shutterbug.gui.tools.base_tool import BaseTool
from shutterbug.gui.panels.collapsible_section import CollapsibleSection
from shutterbug.core.LUTs.registry import STRETCH_REGISTRY


class Properties(QWidget):
    def __init__(self, controller: AppController):
        super().__init__()
        self.setObjectName("properties")

        layout = QVBoxLayout()
        self.setLayout(layout)
        # styling
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        # Stacked tabs for that Blender goodness
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        self.tabs.setTabPosition(QTabWidget.TabPosition.West)

        # Different property panels
        self.tool_properties = ToolPropertiesPanel(controller)
        self.image_properties = ImagePropertiesPanel(controller)
        self.graph_properties = GraphPropertiesPanel(controller)
        # We need some icons too
        tool_icon = controller.icons.get_rotated("tool", 90)
        image_icon = controller.icons.get_rotated("image", 90)
        graph_icon = controller.icons.get_rotated("chart", 90)

        self.tabs.addTab(self.tool_properties, tool_icon, "")
        self.tabs.addTab(self.image_properties, image_icon, "")
        self.tabs.addTab(self.graph_properties, graph_icon, "")

        self.tabs.setCurrentWidget(self.tool_properties)

        logging.debug("Tool settings initialized")


class ImagePropertiesPanel(QWidget):

    def __init__(self, controller: AppController):
        super().__init__()

        self.controller = controller
        self._undo_stack = controller._undo_stack

        self.current_image = None

        self.setObjectName("imageProperties")
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        # Set layout styling
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
            self.controller,
            self,
        )

        layout.addWidget(self.settings_panel)

        # Signals to slots
        self.brightness_slider.valueChanged.connect(self._on_brightness_changed)
        self.contrast_slider.valueChanged.connect(self._on_contrast_changed)
        self.stretches.activated.connect(self._on_stretch_changed)

        controller.on("image.selected", self._on_image_selected)
        controller.on(
            "image.updated.brightness",
            lambda evt: self.brightness_slider.set_value(evt.data.brightness),
        )
        controller.on(
            "image.updated.contrast",
            lambda evt: self.contrast_slider.set_value(evt.data.contrast),
        )
        controller.on(
            "image.updated.stretch_type",
            lambda evt: self.stretches.set_text(evt.data.stretch_type),
        )

        logging.debug("Image properties panel initialized")

    @Slot(Event)
    def _on_image_selected(self, event: Event):
        """Handles image changing in image manager"""
        image = event.data

        if image:
            # Add new subscriptions and set the slider values
            self.current_image = image
            self.brightness_slider.set_value(image.brightness)
            self.contrast_slider.set_value(image.contrast)
            self.stretches.set_text(image.stretch_type)

    @Slot(int)
    def _on_brightness_changed(self, value: int):
        if self.current_image:
            self._undo_stack.push(
                SetImageValueCommand("brightness", value, self.current_image)
            )

    @Slot(int)
    def _on_contrast_changed(self, value: int):
        if self.current_image:
            self._undo_stack.push(
                SetImageValueCommand("contrast", value, self.current_image)
            )

    @Slot(str)
    def _on_stretch_changed(self, value: str):
        if self.current_image:
            self._undo_stack.push(
                SetImageValueCommand("stretch_type", value, self.current_image)
            )


class GraphPropertiesPanel(QWidget):
    def __init__(self, controller: AppController):
        super().__init__()
        # General variables and settings
        self.setObjectName("graphProperties")
        self.current_graph = None
        self.controller = controller

        # Layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        # Set layout styling
        layout.setContentsMargins(16, 8, 8, 8)
        layout.setSpacing(5)

        # Set up controls
        self.title = LabeledTextBox("Title")
        self.x_label = LabeledTextBox("X Label")
        self.y_label = LabeledTextBox("Y Label")

        self.panel = CollapsibleSection(
            "Graph Settings", [self.title, self.x_label, self.y_label], controller, self
        )

        layout.addWidget(self.panel)

        # Handle signals
        controller.on("graph.selected", self._on_graph_selected)
        controller.on(
            "graph.updated.title", lambda evt: self.title.set_text(evt.data.title)
        )
        controller.on(
            "graph.updated.x_label", lambda evt: self.title.set_text(evt.data.x_label)
        )
        controller.on(
            "graph.updated.y_label", lambda evt: self.title.set_text(evt.data.y_label)
        )

        logging.debug("Graph Properties panel initialized")

    @Slot(Event)
    def _on_graph_selected(self, event: Event):
        """Handles new graph being selected"""
        graph = event.data
        self.current_graph = graph
        if graph:
            self.title.set_text(graph.title)
            self.x_label.set_text(graph.x_label)
            self.y_label.set_text(graph.y_label)

    @Slot(str)
    def _on_title_changed(self, title: str):
        """Handles title changing in graph"""
        if self.current_graph:
            self.controller._undo_stack.push(
                SetGraphValueCommand("title", title, self.current_graph)
            )

    @Slot(str)
    def _on_x_label_changed(self, label: str):
        """Handles X label changing in graph"""
        if self.current_graph:
            self.controller._undo_stack.push(
                SetGraphValueCommand("x_label", label, self.current_graph)
            )

    @Slot(str)
    def _on_y_label_changed(self, label: str):
        """Handles Y label changing in graph"""
        if self.current_graph:
            self.controller._undo_stack.push(
                SetGraphValueCommand("y_label", label, self.current_graph)
            )


class ToolPropertiesPanel(QWidget):
    def __init__(self, controller: AppController):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.controller = controller

        layout.setContentsMargins(16, 8, 8, 8)
        layout.setSpacing(5)
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        controller.on("tool.selected", lambda x: self.set_panel(x.data))

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
                section = CollapsibleSection(
                    "Options", [settings], self.controller, self
                )
                layout.addWidget(section)
