from shutterbug.core.app_controller import AppController
from shutterbug.core.events.change_event import Event
import logging

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QLabel, QTabWidget, QVBoxLayout
from shutterbug.gui.base_ui_widget import BaseUIWidget
from shutterbug.gui.commands import SetGraphValueCommand, SetImageValueCommand
from shutterbug.gui.controls import LabeledSlider, LabeledComboBox
from shutterbug.gui.controls.labeled_text_box import LabeledTextBox
from shutterbug.gui.tools.base_tool import BaseTool
from shutterbug.gui.panels.collapsible_section import CollapsibleSection
from shutterbug.core.LUTs.registry import STRETCH_REGISTRY
from shutterbug.gui.views.registry import register_view
from .base_view import BaseView


@register_view()
class Properties(BaseView):
    name = "Properties"

    def __init__(self, controller: AppController, parent=None):
        super().__init__(controller, parent)
        self.setObjectName("properties")

        layout = QVBoxLayout()
        self.setLayout(layout)
        # styling
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        # Stacked tabs for that Blender goodness
        self.tabs = QTabWidget()
        self.tabs.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.tabs.setAutoFillBackground(True)
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

    def on_activated(self):
        """Handles creation of properties view"""
        self.image_properties.on_activated()
        self.tool_properties.on_activated()
        self.graph_properties.on_activated()

    def on_deactivated(self):
        """Handles destruction of properties view"""
        super().on_deactivated()
        self.image_properties.on_deactivated()
        self.tool_properties.on_deactivated()
        self.graph_properties.on_deactivated()


class ImagePropertiesPanel(BaseUIWidget):

    def __init__(self, controller: AppController, parent=None):
        super().__init__(controller, parent)

        self.controller = controller
        self._undo_stack = controller._undo_stack

        self.current_image = controller.selections.image

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

        # Set up sliders
        if self.current_image:
            self.stretches.set_text(self.current_image.stretch_type)
            self.brightness_slider.set_value(self.current_image.brightness)
            self.contrast_slider.set_value(self.current_image.contrast)

        logging.debug("Image properties panel initialized")

    def on_activated(self):
        """Handles activation of image properties panel"""
        # Signals to slots
        self.brightness_slider.valueChanged.connect(self._on_brightness_changed)
        self.contrast_slider.valueChanged.connect(self._on_contrast_changed)
        self.stretches.activated.connect(self._on_stretch_changed)

        self.subscribe("image.selected", self._on_image_selected)
        self.subscribe(
            "image.updated.brightness",
            lambda evt: self.brightness_slider.set_value(evt.data.brightness),
        )
        self.subscribe(
            "image.updated.contrast",
            lambda evt: self.contrast_slider.set_value(evt.data.contrast),
        )
        self.subscribe(
            "image.updated.stretch_type",
            lambda evt: self.stretches.set_text(evt.data.stretch_type),
        )

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


class GraphPropertiesPanel(BaseUIWidget):
    def __init__(self, controller: AppController, parent=None):
        super().__init__(controller, parent)
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

        logging.debug("Graph Properties panel initialized")

    def on_activated(self):
        """Handles creation of graph properties panel"""
        # Handle signals
        self.subscribe("graph.selected", self._on_graph_selected)
        self.subscribe(
            "graph.updated.title", lambda evt: self.title.set_text(evt.data.title)
        )
        self.subscribe(
            "graph.updated.x_label", lambda evt: self.title.set_text(evt.data.x_label)
        )
        self.subscribe(
            "graph.updated.y_label", lambda evt: self.title.set_text(evt.data.y_label)
        )

        self.title.editing_finished.connect(self._on_title_changed)
        self.x_label.editing_finished.connect(self._on_x_label_changed)
        self.y_label.editing_finished.connect(self._on_y_label_changed)

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


class ToolPropertiesPanel(BaseUIWidget):
    def __init__(self, controller: AppController, parent=None):
        super().__init__(controller, parent)
        # Layout settings
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.setObjectName("toolProperties")
        self.controller = controller

        layout.setContentsMargins(16, 8, 8, 8)
        layout.setSpacing(5)
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        current_tool = self.controller.tools._current_tool
        if current_tool:
            self.set_panel(current_tool)

        logging.debug("Tool properties panel initialized")

    def on_activated(self):
        """Handles creation of tool properties pane"""
        self.subscribe("tool.selected", lambda x: self.set_panel(x.data))

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
