from __future__ import annotations

from typing import TYPE_CHECKING

from shutterbug.core.models.marker_model import MarkerModel
from shutterbug.gui.commands.star_commands import PropagateStarSelection


if TYPE_CHECKING:
    from shutterbug.core.app_controller import AppController

import logging
from typing import Tuple

from PySide6.QtCore import (
    Property,
    QPoint,
    QPointF,
    QPropertyAnimation,
    QRect,
    Qt,
    Signal,
    Slot,
)
from PySide6.QtGui import (
    QContextMenuEvent,
    QImage,
    QKeyEvent,
    QMouseEvent,
    QPen,
    QPixmap,
    QWheelEvent,
)
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView, QMenu, QVBoxLayout, QWidget

from shutterbug.core.models import FITSModel
from shutterbug.core.events.change_event import Event
from shutterbug.core.managers import StretchManager
from shutterbug.gui.commands import DifferentialPhotometryCommand
from shutterbug.gui.panels import BasePopOver, OperatorPanel, ToolPanel
from shutterbug.gui.tools import SelectTool
from shutterbug.gui.managers import ToolManager
from .base_view import BaseView
from shutterbug.gui.views.registry import register_view


@register_view()
class ImageViewer(BaseView):

    name = "Image Viewer"
    # Tool signals
    tool_settings_changed = Signal(QWidget)

    def __init__(self, controller: AppController, parent=None):
        super().__init__(controller, parent)
        # Initial variables
        self.setObjectName("viewer")

        self.view = ImageGraphicsView(controller, self)

        # Layout and styling
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.view)

        # Manager setup
        self._undo_stack = controller._undo_stack
        self.catalog = controller.stars
        self.image_manager = controller.images
        self.tools = ToolManager(controller)

        self.tools.set_tool(SelectTool)

        # Popover panel
        self.popover = ToolPanel(controller, self)
        self._toggle_popover(self.popover)
        self.op_panel = OperatorPanel(controller, self)

        # General signals

        # Tool signals
        self.controller.on("operator.selected", self._on_operator_changed)
        self.controller.on("operator.finished", self._on_operator_finished)
        self.controller.on("operator.cancelled", self._on_operator_finished)

        self.tools.tool_settings_changed.connect(self.tool_settings_changed)

        self.popover.tool_selected.connect(self.tools.set_tool)

        logging.debug("Image Viewer initialized")

    @Slot(Event)
    def _on_operator_changed(self, event: Event):
        """Handles operator changing in Tool Manager"""
        operator = event.data
        if operator is None:
            logging.debug("No operator given on change")
            return
        self.op_panel.set_panel(operator)
        self._toggle_popover(self.op_panel)

    @Slot(Event)
    def _on_operator_finished(self, _: Event):
        """Handles operator being finished or cancelled"""
        self.op_panel.hide()

    @Slot()
    def _on_differential(self):
        """Handles differential photometry on image being requested"""
        if self.view.current_image is None:
            return  # No work to do

        self.controller._undo_stack.push(
            DifferentialPhotometryCommand(self.view.current_image, self.controller)
        )

    @Slot()
    def _on_propagate(self):
        """Handles propagating measurements request"""
        if self.view.current_image is None:
            return  # No work to do

        self.controller._undo_stack.push(
            PropagateStarSelection(self.view.current_image, self.controller)
        )

    @Slot(QMouseEvent)
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.tools.end_operation_confirm()
            self.tools.begin_operation(event, self)
            event.accept()
        else:
            super().mousePressEvent(event)

    @Slot(QMouseEvent)
    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.tools.end_operation_interaction()
            event.accept()

    @Slot(QMouseEvent)
    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        self.tools.update_operation(event)
        event.accept()

    @Slot(QKeyEvent)
    def keyPressEvent(self, event: QKeyEvent):
        """Handles keypress events"""
        if event.key() == Qt.Key.Key_N:
            self._toggle_popover(self.popover)
        if event.key() == Qt.Key.Key_Escape:
            self.tools.end_operation_cancel()

        if event.key() == Qt.Key.Key_Enter:
            self.tools.end_operation_confirm()

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        menu = QMenu()

        differential_action = menu.addAction("Differential Photometry")
        differential_action.triggered.connect(self._on_differential)

        propagate_action = menu.addAction("Propagate Measurements")
        propagate_action.triggered.connect(self._on_propagate)

        menu.exec(event.globalPos())

        super().contextMenuEvent(event)

    def _toggle_popover(self, panel: BasePopOver):
        """Toggles popover panel"""
        if panel.isVisible():
            panel.hide()
        else:
            panel.show_at_corner()


class ImageGraphicsView(QGraphicsView):

    # Zoom defaults
    ZOOM_FACTOR_DEFAULT = 1.1
    ZOOM_MAXIMUM_DEFAULT = 10.0
    ZOOM_MINIMUM_DEFAULT = 0.5

    def __init__(self, controller: AppController, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.current_image = None
        self.first_image = True

        self.markers = {}  # (x, y) -> List[marker]

        # Manager setup
        self.stretchs = StretchManager(controller)
        self.image_manager = controller.images

        # Scene setup
        scene = QGraphicsScene(self)
        self.setScene(scene)
        self.pixmap_item = scene.addPixmap(QPixmap())

        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # No drag initially, we will capture middle mouse and drag then
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        # Scrollbars look ugly here
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Set up zooming behavior
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

        # Zoom settings
        self.zoom_factor = self.ZOOM_FACTOR_DEFAULT
        self.zoom_max = self.ZOOM_MAXIMUM_DEFAULT
        self.zoom_min = self.ZOOM_MINIMUM_DEFAULT
        self.scale(1.0, 1.0)  # Scale of 1

        # Zoom animation settings
        self._zoom_level = 1.0  # base scale
        self._target_scene_pos = QPointF()
        self._target_viewport_pos = QPointF()
        self.anim = None

        # General signals
        self.controller.on("image.selected", self._on_image_selected)
        self.controller.on("image.updated.*", self._on_image_update_event)
        self.controller.on("marker.created", self._on_marker_created)
        self.controller.on("marker.removed", self._on_marker_removed)
        self.controller.on("marker.updated.*", self._on_marker_updated)

    @Slot(Event)
    def _on_image_selected(self, event: Event):
        """Handles image manager active image changing"""
        image = event.data
        if image != self.current_image:

            self.current_image = image
            if image is not None:
                self.stretchs.brightness = image.brightness
                self.stretchs.contrast = image.contrast
                self.stretchs.set_mode(image.stretch_type)
                self.stretchs.update_lut()

            self.update_display()

    @Slot(Event)
    def _on_image_update_event(self, event: Event):
        """Handles current image changing values"""
        image = event.data
        if image is None:
            return
        if image == self.current_image:
            self.stretchs.brightness = image.brightness
            self.stretchs.contrast = image.contrast
            self.stretchs.set_mode(image.stretch_type)
            self.stretchs.update_lut()
            self.update_display()

    @Slot(Event)
    def _on_marker_created(self, event: Event):
        marker = event.data
        if marker is None or self.current_image is None:
            return
        if marker.image_id != self.current_image.uid:
            return

        self.add_star_marker(marker)

    @Slot(Event)
    def _on_marker_removed(self, event: Event):
        marker = event.data
        if marker is None or self.current_image is None:
            return

        self.remove_star_marker(marker)

    @Slot(Event)
    def _on_marker_updated(self, event: Event):
        marker = event.data
        if marker is None or self.current_image is None:
            return
        if marker.image_id != self.current_image.uid:
            return

        # Lazy way, need to revise
        self.remove_star_marker(marker)
        self.add_star_marker(marker)

    # Zoom properties for animation
    def get_zoom(self):
        """Gets zoom level"""
        return self._zoom_level

    def set_zoom(self, value: float):
        """Sets zoom level"""
        if self._zoom_level == 0:
            return

        factor = value / self._zoom_level
        self._zoom_level = value
        self.scale(factor, factor)

        # Correct for mouse changing position
        delta = (
            self.mapToScene(self._target_viewport_pos.toPoint())
            - self._target_scene_pos
        )
        self.translate(delta.x(), delta.y())

    zoom = Property(float, get_zoom, set_zoom)

    @Slot(QWheelEvent)
    def wheelEvent(self, event: QWheelEvent):
        # Are we zooming in or out?
        zoom = event.angleDelta().y() > 0
        factor = self.zoom_factor if zoom else 1 / self.zoom_factor

        # Limit zoom
        current_scale = self._zoom_level
        new_scale = current_scale * factor
        if new_scale >= self.zoom_max or new_scale <= self.zoom_min:
            return  # Limit zoom level

        # Get old position first
        self._target_viewport_pos = event.position()
        self._target_viewport_pos = self.mapToScene(event.position().toPoint())

        # Kill any running animation
        if self.anim and self.anim.state() == QPropertyAnimation.State.Running:
            self.anim.stop()

        # Animate the zoom change
        self.anim = QPropertyAnimation(self, b"zoom")
        self.anim.setDuration(10)  # Tweak for feel
        self.anim.setStartValue(self._zoom_level)
        self.anim.setEndValue(new_scale)
        self.anim.start()

    @Slot(QMouseEvent)
    def mousePressEvent(self, event: QMouseEvent):
        if self.current_image is None:
            return None
        if event.button() == Qt.MouseButton.MiddleButton:
            # start panning
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
            # Fake left-mousebutton for dragging
            fake_event = QMouseEvent(
                event.type(),
                event.position(),
                Qt.MouseButton.LeftButton,
                Qt.MouseButton.LeftButton,
                event.modifiers(),
            )
            super().mousePressEvent(fake_event)
        super().mousePressEvent(event)

    @Slot(QMouseEvent)
    def mouseReleaseEvent(self, event: QMouseEvent):
        if self.current_image is None:
            return None
        if event.button() == Qt.MouseButton.MiddleButton:
            # Stop panning
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
        super().mouseReleaseEvent(event)

    @Slot(QMouseEvent)
    def mouseMoveEvent(self, event: QMouseEvent):
        if self.parent():
            # We know the parent exists and that the parent has
            # this class
            self.parent().mouseMoveEvent(event)  # type: ignore
        super().mouseMoveEvent(event)

    def update_display(self):
        """Updates image display"""
        if self.current_image is None:
            self.pixmap_item.setPixmap(QPixmap())
            return

        self._display_image(self.current_image)

    def get_8bit_preview(self):
        """Gets the 8bit display version of the image data"""
        image = self.current_image
        if image is None:
            return None

        display_data = self.stretchs.apply(image.display_data)
        return display_data

    def _display_image(self, image: FITSModel):
        """Display given FITS data array"""
        logging.debug(f"Image display called on image: {image.filename}")
        self._clear_markers()

        old_center = self.mapToScene(self.viewport().rect().center())

        # Store new image
        self.current_image = image

        # Get normalized information
        display_data = self.get_8bit_preview()
        if display_data is None:
            return  # No work to do!
        logging.debug(f"Data normalized, attempting to display")
        # Convert to QImage
        height, width = display_data.shape
        qimage = QImage(display_data, width, height, QImage.Format.Format_Grayscale8)  # type: ignore

        # Display
        pixmap = QPixmap.fromImage(qimage)
        self.pixmap_item.setPixmap(pixmap)
        if self.first_image:
            self.fitInView(self.pixmap_item, Qt.AspectRatioMode.KeepAspectRatio)
            self.first_image = False

        self.centerOn(old_center)
        new_center = self.mapToScene(self.viewport().rect().center())
        # Fixing upward drift
        delta = old_center - new_center
        self.centerOn(old_center + delta)
        self._display_markers_for_image()

    def _clear_image(self):
        """Clear current image from view"""
        self.current_image = None
        self._clear_markers()
        self.pixmap_item.setPixmap(QPixmap())

    def _display_markers_for_image(self):
        """Restore markers from image state"""
        # Add markers from image
        if self.current_image is None:
            return

        markers = self.controller.markers.markers_from_image(self.current_image)
        for marker in markers:
            self.add_star_marker(marker)

    def _clear_markers(self):
        """Remove all star markers"""
        for item in self.markers.values():
            self.scene().removeItem(item)

        self.markers = {}

    def add_star_marker(self, marker: MarkerModel):
        """Add a circular marker at image coordinates x, y"""
        # Create circle
        pen = QPen(marker.colour)
        pen.setWidth(marker.thickness)

        circle = self.scene().addEllipse(
            marker.rect,
            pen,
        )
        if not marker.visible:
            circle.hide()

        self.markers[marker.id] = circle

    def remove_star_marker(self, marker: MarkerModel):
        """Remove a circular marker at image coordinates x, y"""

        if marker.id in self.markers:
            item = self.markers.pop(marker.id)
            self.scene().removeItem(item)

    def _convert_to_image_coordinates(self, coordinate: QPoint) -> Tuple[float, float]:
        """Converts coordinates of click to coordinates of active image"""
        # Step 1, convert to scene coordinates
        scene_pos = self.mapToScene(coordinate).toPoint()
        # Step 2, there is no step 2
        return scene_pos.x(), scene_pos.y()

    def viewport_rect_to_scene(self, rect: QRect) -> QRect:
        """Converts a rect to scene coordinates"""
        poly = self.mapToScene(rect)
        return poly.boundingRect().toRect()

    def get_centroid_at_point(self, coordinates: QPoint):
        """Gets star, if any, under point"""
        image = self.current_image
        if image is None:
            # No work to do
            return None

        x, y = self._convert_to_image_coordinates(coordinates)
        logging.debug(f"Attempting to select centroid at ({x}, {y})")

        centroid = self.image_manager.find_nearest_centroid(image, x, y)

        return centroid
