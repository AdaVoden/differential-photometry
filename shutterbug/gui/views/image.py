import logging
from typing import Tuple

from PySide6.QtCore import (
    Property,
    QPoint,
    QPointF,
    QPropertyAnimation,
    Qt,
    Signal,
    Slot,
)
from PySide6.QtGui import (
    QColor,
    QContextMenuEvent,
    QImage,
    QMouseEvent,
    QPen,
    QPixmap,
    QUndoStack,
    QWheelEvent,
)
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView, QMenu

from shutterbug.core.managers.measurement_manager import MeasurementManager
from shutterbug.core.models import FITSModel, StarMeasurement
from shutterbug.core.managers import ImageManager
from shutterbug.core.utility.photometry import measure_star_magnitude
from shutterbug.gui.commands import RemoveMeasurementCommand, AddMeasurementCommand

import numpy as np


class ImageViewer(QGraphicsView):

    propagation_requested = Signal(FITSModel)
    batch_requested = Signal()

    # Zoom defaults
    ZOOM_FACTOR_DEFAULT = 1.1
    ZOOM_MAXIMUM_DEFAULT = 7.5
    ZOOM_MINIMUM_DEFAULT = 0.5

    # Marker defaults
    MARKER_COLOUR_DEFAULT = "cyan"
    MARKER_RADIUS_DEFAULT = 20  # pixels

    def __init__(self, undo_stack: QUndoStack):
        super().__init__()
        # Initial variables
        self.setObjectName("viewer")

        self._undo_stack = undo_stack
        self.image_manager = ImageManager()
        self.measure_manager = MeasurementManager()

        self.current_image = self.image_manager.active_image
        self.markers = {}  # (x, y) -> marker

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

        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Set up scene
        scene = QGraphicsScene(self)
        self.setScene(scene)

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

        # Set up signals
        self.image_manager.active_image_changed.connect(self._on_image_changed)

        logging.debug("Image Viewer initialized")

    def _on_image_changed(self, image: FITSModel):
        """Handles image manager active image changing"""
        measure_manager = self.measure_manager
        if self.current_image:
            self.current_image.updated.disconnect(self.update_display)
            self.current_image.updated.disconnect(self.update_display)
            measure_manager.measurement_added.disconnect(self.add_star_marker)
            measure_manager.measurement_removed.disconnect(self.remove_star_marker)

        self.current_image = image
        if image:
            image.updated.connect(self.update_display)
            image.updated.connect(self.update_display)
            measure_manager.measurement_added.connect(self.add_star_marker)
            measure_manager.measurement_removed.connect(self.remove_star_marker)

        self.update_display()

    # Zoom properties for animation
    def get_zoom(self):
        return self._zoom_level

    def set_zoom(self, value: float):
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
        self.anim.setDuration(25)  # Tweak for feel
        self.anim.setStartValue(self._zoom_level)
        self.anim.setEndValue(new_scale)
        self.anim.start()

    def mousePressEvent(self, event: QMouseEvent):
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
            # Normal left click
            self._on_viewer_clicked(event)
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.MiddleButton:
            # Stop panning
            self.setDragMode(QGraphicsView.DragMode.NoDrag)

        super().mouseReleaseEvent(event)

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        menu = QMenu()

        # select_star_action = menu.addAction("Select as Target Star")

        find_stars_action = menu.addAction("Find all stars in image")
        find_stars_action.triggered.connect(self.find_stars_in_image)

        calc_phot_action = menu.addAction("Calculate magnitude for selected star")
        calc_phot_action.triggered.connect(self._on_photometry_requested)

        propagate_action = menu.addAction("Propagate star selection")
        propagate_action.triggered.connect(self.on_propagate_requested)

        process_action = menu.addAction("Batch process all images")
        process_action.triggered.connect(self.batch_requested)

        menu.exec(event.globalPos())

        super().contextMenuEvent(event)

    @Slot(QMouseEvent)
    def _on_viewer_clicked(self, event: QMouseEvent):
        """Handler for a click in the viewer"""
        current_image = self.image_manager.active_image
        if current_image is None:
            # No image, we don't care
            return

        # Alt + Click, remove a star
        if event.modifiers() == Qt.KeyboardModifier.AltModifier:
            if event.button() == Qt.MouseButton.LeftButton:
                self.deselect_star(event.pos())
            return

        if event.button() == Qt.MouseButton.LeftButton:
            self.select_star(event.pos())
            return

    @Slot()
    def _on_photometry_requested(self):
        """Handles photometry being requested on stars"""
        if self.current_image is None:
            return  # No work to do

        measurement_manager = self.measure_manager
        image_name = self.current_image.filename

        stars = measurement_manager.get_all_measurements(image_name)
        for star in stars:
            measure_star_magnitude(star, data=self.current_image.data)

    @Slot()
    def find_stars_in_image(self):
        if self.current_image is None:
            return  # No work to do

        self.image_manager.find_stars()

    def get_star(self, coordinates: QPoint):
        """Gets star, if any, under point"""
        image = self.image_manager.active_image
        if image is None:
            # No work to do
            return None

        x, y = self._convert_to_image_coordinates(coordinates)

        star = self.image_manager.find_nearest_star(x, y)

        return star

    def get_measurement(self, coordinates: QPoint):
        """Gets already registered measurement at point, if any"""
        measure_manager = self.measure_manager
        image = self.current_image
        if image is None:
            return None  # No work to do

        x, y = self._convert_to_image_coordinates(coordinates)

        measurement = measure_manager.find_nearest(image.filename, x, y)

        return measurement

    def select_star(self, coordinates: QPoint):
        """Creates the select star command and pushes command to the stack"""
        logging.debug(
            f"Attempting to select star at {coordinates.x()}/{coordinates.y()}"
        )
        star = self.get_star(coordinates)
        current_image = self.image_manager.active_image

        if star is None or current_image is None:
            logging.debug("No star found or current image is not set")
            return  # No work to do
        logging.debug("Star found, creating command")

        self._undo_stack.push(AddMeasurementCommand(star, current_image))

    def deselect_star(self, coordinates: QPoint):
        """Creates the deselect star command and pushes command to the stack"""
        logging.debug(
            f"Attempting to deselect star at {coordinates.x()}/{coordinates.y()}"
        )
        current_image = self.image_manager.active_image
        measurement = self.get_measurement(coordinates)

        if measurement is None or current_image is None:
            logging.debug("No star found or current image is not set")
            return  # No work to do
        logging.debug("Star found, creating command")

        self._undo_stack.push(RemoveMeasurementCommand(measurement))

    @Slot()
    def on_propagate_requested(self):
        if not self.current_image:
            return None

        self.propagation_requested.emit(self.current_image)

    def _convert_to_image_coordinates(self, coordinate: QPoint) -> Tuple[float, float]:
        """Converts coordinates of click to coordinates of active image"""
        # Step 1, convert to scene coordinates
        scene_pos = self.mapToScene(coordinate)

        # Step 2, map to Pixmap
        pix_pos = self.pixmap_item.mapToScene(scene_pos)

        # Step 3, there is no step 3
        return pix_pos.x(), pix_pos.y()

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
        old_zoom = self._zoom_level

        # Store new image
        self.current_image = image

        # Get normalized information
        display_data = self.get_normalized_data()
        if display_data is None:
            return  # No work to do!

        # Convert to QImage
        height, width = display_data.shape
        qimage = QImage(
            display_data.data, width, height, QImage.Format.Format_Grayscale8
        )

        # Display
        pixmap = QPixmap.fromImage(qimage)
        self.pixmap_item.setPixmap(pixmap)
        self.fitInView(self.pixmap_item, Qt.AspectRatioMode.KeepAspectRatio)

        # Keep same view
        self._zoom_level = old_zoom
        self.scale(old_zoom, old_zoom)
        self.centerOn(old_center)

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

        stars = self.measure_manager.get_all_measurements(image_name)
        for star in stars:
            self.add_star_marker(star, colour="cyan")

    @Slot()
    def update_display(self):
        if self.current_image is None:
            self.pixmap_item.setPixmap(QPixmap())
            return

        self._display_image(self.current_image)

    def get_normalized_data(self):
        """Normalize the FITS data to 0-255 for display"""
        if self.current_image is None:
            return  # No image = no data

        data = self.current_image.display_data.astype(np.float32)
        brightness = self.current_image.brightness
        contrast = self.current_image.contrast
        # apply brightness/contrast

        data = data * contrast

        data = data + brightness

        data = np.clip(data, 0, 255).astype(np.uint8)

        return data
