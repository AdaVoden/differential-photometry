from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from shutterbug.gui.main_window import MainWindow

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
    QColor,
    QContextMenuEvent,
    QImage,
    QKeyEvent,
    QMouseEvent,
    QPen,
    QPixmap,
    QWheelEvent,
)
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView, QMenu, QWidget
from shutterbug.core.events import ImageUpdateEvent
from shutterbug.core.managers import (
    StretchManager,
)
from shutterbug.core.models import FITSModel, StarIdentity, StarMeasurement
from shutterbug.core.utility.photometry import measure_star_magnitude
from shutterbug.gui.commands import (
    AddMeasurementsCommand,
    RemoveMeasurementCommand,
    SelectStarCommand,
)
from shutterbug.gui.managers import ToolManager
from shutterbug.gui.operators import BaseOperator
from shutterbug.gui.panels import BasePopOver, OperatorPanel, ToolPanel
from shutterbug.gui.tools import BaseTool, SelectTool


class ImageViewer(QGraphicsView):

    propagation_requested = Signal(FITSModel)
    batch_requested = Signal()
    tool_changed = Signal(BaseTool)
    tool_settings_changed = Signal(QWidget)

    # Zoom defaults
    ZOOM_FACTOR_DEFAULT = 1.1
    ZOOM_MAXIMUM_DEFAULT = 7.5
    ZOOM_MINIMUM_DEFAULT = 0.5

    # Marker defaults
    MARKER_COLOUR_DEFAULT = "cyan"
    MARKER_RADIUS_DEFAULT = 20  # pixels

    def __init__(self, main_window: MainWindow):
        super().__init__()
        # Initial variables
        self.setObjectName("viewer")
        self.current_image = None
        self.selected_star = None
        self.markers = {}  # (x, y) -> marker
        self.main_window = main_window

        # Manager setup
        self._undo_stack = main_window._undo_stack
        self.catalog = main_window.star_catalog
        self.image_manager = main_window.image_manager
        self.tool_manager = ToolManager(self)
        self.stretch_manager = StretchManager()
        self.tool_manager.set_tool(SelectTool)

        # Zoom settings
        self.zoom_factor = self.ZOOM_FACTOR_DEFAULT
        self.zoom_max = self.ZOOM_MAXIMUM_DEFAULT
        self.zoom_min = self.ZOOM_MINIMUM_DEFAULT
        self.scale(1.0, 1.0)  # Scale of 1
        self.first_image = True

        # Zoom animation settings
        self._zoom_level = 1.0  # base scale
        self._target_scene_pos = QPointF()
        self._target_viewport_pos = QPointF()
        self.anim = None

        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Set up scene
        scene = QGraphicsScene(self)
        self.setScene(scene)

        # Popover panel
        self.popover = ToolPanel(self)
        self.op_panel = OperatorPanel(self)

        # Add pixmap item to scene, blank for now
        self.pixmap_item = scene.addPixmap(QPixmap())

        # Set up panning and scrolling
        # No drag initially, we will capture middle mouse and drag then
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        # Scrollbars look ugly here
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Set up zooming behavior
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

        # General signals
        self.main_window.image_selected.connect(self._on_image_selected)
        self.main_window.measurement_added.connect(self.add_star_marker)
        self.main_window.measurement_removed.connect(self.remove_star_marker)
        self.main_window.star_selected.connect(self._on_star_selected)

        # Tool signals
        self.tool_manager.tool_changed.connect(self._on_tool_changed)
        self.tool_manager.tool_settings_changed.connect(self.tool_settings_changed)
        self.tool_manager.operator_changed.connect(self._on_operator_changed)
        self.tool_manager.operator_finished.connect(self._on_operator_finished)
        self.tool_manager.operator_cancelled.connect(self._on_operator_finished)

        self.popover.tool_selected.connect(self.tool_manager.set_tool)

        logging.debug("Image Viewer initialized")

    @Slot(FITSModel)
    def _on_image_selected(self, image: FITSModel):
        """Handles image manager active image changing"""
        if image != self.current_image:
            if self.current_image:
                self.current_image.updated.disconnect(self._on_image_update_event)

            self.current_image = image
            if image is not None:
                image.updated.connect(self._on_image_update_event)
                self.stretch_manager.brightness = image.brightness
                self.stretch_manager.contrast = image.contrast
                self.stretch_manager.set_mode(image.stretch_type)
                self.stretch_manager.update_lut()

            self.update_display()

    @Slot(StarIdentity)
    def _on_star_selected(self, star: StarIdentity):
        """Handles star being selected"""
        if self.current_image is None:
            return  # Need an image for this

        if self.selected_star is not None:
            # Add back in unselected star
            self.remove_star_marker(self.selected_star)
            self.add_star_marker(self.selected_star)

        measurement = star.measurements.get(self.current_image.filename)
        self.selected_star = measurement
        if measurement is None:
            return  # Image does not have this measurement
        self.remove_star_marker(measurement)
        self.add_star_marker(measurement, colour="gold")

    @Slot(ImageUpdateEvent)
    def _on_image_update_event(self, event: ImageUpdateEvent):
        """Handles current image changing values"""
        fields = event.changed_fields
        image = event.source
        if fields & {"brightness", "contrast"}:
            self.stretch_manager.brightness = image.brightness
            self.stretch_manager.contrast = image.contrast
        if fields & {"stretch_type"}:
            self.stretch_manager.set_mode(image.stretch_type)

        self.stretch_manager.update_lut()
        self.update_display()

    @Slot(BaseTool)
    def _on_tool_changed(self, tool: BaseTool):
        """Handles tool changing in Tool Manager"""
        self.tool_changed.emit(tool)

    @Slot(BaseOperator)
    def _on_operator_changed(self, operator: BaseOperator):
        """Handles operator changing in Tool Manager"""
        self.op_panel.set_panel(operator)
        self._toggle_popover(self.op_panel)

    @Slot()
    def _on_operator_finished(self):
        """Handles operator being finished or cancelled"""
        self.op_panel.hide()

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
        else:
            if event.button() == Qt.MouseButton.LeftButton:
                self.tool_manager.end_operation_confirm()
                self.tool_manager.begin_operation(event)
            super().mousePressEvent(event)

    @Slot(QMouseEvent)
    def mouseReleaseEvent(self, event: QMouseEvent):
        if self.current_image is None:
            return None
        if event.button() == Qt.MouseButton.MiddleButton:
            # Stop panning
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
        if event.button() == Qt.MouseButton.LeftButton:
            self.tool_manager.end_operation_interaction()
        super().mouseReleaseEvent(event)

    @Slot(QMouseEvent)
    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self.current_image is None:
            return None
        self.tool_manager.update_operation(event)

        super().mouseMoveEvent(event)

    @Slot(QKeyEvent)
    def keyPressEvent(self, event: QKeyEvent):
        """Handles keypress events"""
        if event.key() == Qt.Key.Key_N:
            self._toggle_popover(self.popover)
        if event.key() == Qt.Key.Key_Escape:
            self.tool_manager.end_operation_cancel()

        if event.key() == Qt.Key.Key_Enter:
            self.tool_manager.end_operation_confirm()

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        menu = QMenu()

        calc_phot_action = menu.addAction("Calculate magnitude for selected star")
        calc_phot_action.triggered.connect(self._on_photometry_requested)

        propagate_action = menu.addAction("Propagate star selection")
        propagate_action.triggered.connect(self._on_propagate_requested)

        process_action = menu.addAction("Batch process all images")
        process_action.triggered.connect(self.batch_requested)

        menu.exec(event.globalPos())

        super().contextMenuEvent(event)

    @Slot()
    def _on_photometry_requested(self):
        """Handles photometry being requested on stars"""
        if self.current_image is None:
            return  # No work to do

        catalog = self.catalog
        image_name = self.current_image.filename

        stars = catalog.get_measurements_by_image(image_name)
        for star in stars:
            measure_star_magnitude(star, data=self.current_image.data)

    def _toggle_popover(self, panel: BasePopOver):
        """Toggles popover panel"""
        if panel.isVisible():
            panel.hide()
        else:
            panel.show_at_corner()

    def get_centroid_at_point(self, coordinates: QPoint):
        """Gets star, if any, under point"""
        image = self.image_manager.active_image
        if image is None:
            # No work to do
            return None

        x, y = self._convert_to_image_coordinates(coordinates)
        logging.debug(f"Attempting to select centroid at {x}/{y}")

        star = self.image_manager.find_nearest_centroid(image, x, y)

        return star

    def get_registered_measurement(self, coordinates: QPoint) -> StarIdentity | None:
        """Gets already registered measurement at point, if any"""
        catalog = self.catalog
        image = self.image_manager.active_image
        if image is None:
            return None  # No work to do

        x, y = self._convert_to_image_coordinates(coordinates)

        star = catalog.find_nearest(x, y)
        if star is None:
            return None

        return star

    def get_star_at_point(self, coordinates: QPoint):
        """Grabs star at selected point"""
        # First check to see if we have any registered at point
        star = self.get_registered_measurement(coordinates)
        if star:
            return star  # Success

        # Second, check if there's a centroid at point
        centroid = self.get_centroid_at_point(coordinates)
        if centroid:
            return centroid

        # Found nothing
        return None

    def select_star(self, coordinates: QPoint):
        """Creates the select star command and pushes command to the stack"""
        current_image = self.image_manager.active_image
        if current_image is None:
            return  # Nothing to do

        star = self.get_star_at_point(coordinates)
        if star is None:
            logging.debug(
                f"No star found under click at point ({coordinates.x()}, {coordinates.y()})"
            )
            return  # No work to do
        if isinstance(star, StarIdentity):
            self._undo_stack.push(SelectStarCommand(star))
        else:
            self._undo_stack.push(AddMeasurementsCommand([star], current_image))

    def deselect_star(self, coordinates: QPoint):
        """Creates the deselect star command and pushes command to the stack"""
        current_image = self.image_manager.active_image
        if current_image is None:
            return  # Nothing to do
        logging.debug(
            f"Attempting to deselect star at {coordinates.x()}/{coordinates.y()}"
        )
        star = self.get_registered_measurement(coordinates)

        if star is None:
            logging.debug(
                f"No star found under click at point ({coordinates.x()}, {coordinates.y()})"
            )
            return  # No work to do

        logging.debug("Star found, creating command")
        measurement = star.measurements.get(current_image.filename)
        if measurement is not None:
            self._undo_stack.push(RemoveMeasurementCommand(measurement))

    @Slot()
    def _on_propagate_requested(self):
        """Handles image propagation being requested"""
        if self.current_image is None:
            return None

        self.propagation_requested.emit(self.current_image)

    def _convert_to_image_coordinates(self, coordinate: QPoint) -> Tuple[float, float]:
        """Converts coordinates of click to coordinates of active image"""
        # Step 1, convert to scene coordinates
        scene_pos = self.mapToScene(coordinate).toPoint()
        # Step 2, there is no step 2
        return scene_pos.x(), scene_pos.y()

    def add_star_marker(
        self,
        star: StarMeasurement,
        radius: int = MARKER_RADIUS_DEFAULT,
        colour: str = MARKER_COLOUR_DEFAULT,
    ):
        """Add a circular marker at image coordinates x, y"""
        logging.debug(
            f"Adding marker at position ({star.x:.1f},{star.y:.1f}), colour: {colour}"
        )
        # Create circle
        pen = QPen(QColor(colour))
        pen.setWidth(2)

        circle = self.scene().addEllipse(
            star.x - radius,
            star.y - radius,  # top-left corner of circle
            radius * 2,
            radius * 2,  # Width, height
            pen,
        )

        self.markers[(star.x, star.y)] = circle

        return circle

    def remove_star_marker(self, star: StarMeasurement):
        """Remove a circular marker at image coordinates x, y"""
        logging.debug(f"Removing marker at position ({star.x:.1f},{star.y:.1f})")

        if (star.x, star.y) in self.markers:
            marker = self.markers.pop((star.x, star.y))
            self.scene().removeItem(marker)

    def _clear_markers(self):
        """Remove all star markers"""
        for x, y in self.markers:
            self.scene().removeItem(self.markers[(x, y)])

        self.markers = {}

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
        image_name = self.current_image.filename

        stars = self.catalog.get_all_stars()
        measurements = []
        for star in stars:
            m = star.measurements.get(image_name)
            if m is not None:
                measurements.append(m)
        for m in measurements:
            self.add_star_marker(m, colour="cyan")

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

        display_data = self.stretch_manager.apply(image.display_data)
        return display_data

    def viewport_rect_to_scene(self, rect: QRect) -> QRect:
        """Converts a rect to scene coordinates"""
        poly = self.mapToScene(rect)
        return poly.boundingRect().toRect()
