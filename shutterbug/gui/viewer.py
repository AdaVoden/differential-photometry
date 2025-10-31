import logging

from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QMenu
from PySide6.QtCore import (
    Qt,
    Slot,
    QPoint,
    Signal,
    QPointF,
    Property,
    QPropertyAnimation,
)
from PySide6.QtGui import (
    QContextMenuEvent,
    QPixmap,
    QImage,
    QPen,
    QColor,
    QMouseEvent,
    QWheelEvent,
)

from shutterbug.gui.image_data import FITSImage

from typing import Tuple


class Viewer(QGraphicsView):

    clicked = Signal(QMouseEvent)
    find_stars_requested = Signal()
    photometry_requested = Signal()
    propagation_requested = Signal(FITSImage)
    batch_requested = Signal()

    # Zoom defaults
    ZOOM_FACTOR_DEFAULT = 1.1
    ZOOM_MAXIMUM_DEFAULT = 5.0
    ZOOM_MINIMUM_DEFAULT = 0.1

    # Marker defaults
    MARKER_COLOUR_DEFAULT = "cyan"
    MARKER_RADIUS_DEFAULT = 20  # pixels

    def __init__(self):
        super().__init__()
        # Initial variables
        self.current_image: FITSImage | None = None
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
        self.setStyleSheet("background-color: black;")

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

        logging.debug("Viewer initialized")

    # Zoom properties for animation
    def get_zoom(self):
        return self._zoom_level

    def set_zoom(self, value: float):
        if self._zoom_level == 0:
            return

        factor = value / self._zoom_level
        self._zoom_level = value
        self.scale(factor, factor)

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
        if new_scale > self.zoom_max or new_scale < self.zoom_min:
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
            self.clicked.emit(event)
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
        find_stars_action.triggered.connect(self.find_stars_requested)

        calc_phot_action = menu.addAction("Calculate magnitude for selected star")
        calc_phot_action.triggered.connect(self.photometry_requested)

        propagate_action = menu.addAction("Propagate star selection")
        propagate_action.triggered.connect(self.on_propagate_requested)

        process_action = menu.addAction("Batch process all images")
        process_action.triggered.connect(self.batch_requested)

        menu.exec(event.globalPos())

        super().contextMenuEvent(event)

    @Slot()
    def on_propagate_requested(self):
        if not self.current_image:
            return None

        self.propagation_requested.emit(self.current_image)

    def convert_to_image_coordinates(self, coordinate: QPoint) -> Tuple[float, float]:
        # Step 1, convert to scene coordinates
        scene_pos = self.mapToScene(coordinate)

        # Step 2, map to Pixmap
        pix_pos = self.pixmap_item.mapToScene(scene_pos)

        # Step 3, there is no step 3
        return pix_pos.x(), pix_pos.y()

    def add_star_marker(
        self,
        x: float,
        y: float,
        radius: int = MARKER_RADIUS_DEFAULT,
        colour: str = MARKER_COLOUR_DEFAULT,
    ):
        """Add a circular marker at image coordinates x, y"""
        logging.debug(f"Adding marker at position ({x:.1f},{y:.1f}), colour: {colour}")
        # Create circle
        pen = QPen(QColor(colour))
        pen.setWidth(2)

        circle = self.scene().addEllipse(
            x - radius,
            y - radius,  # top-left corner of circle
            radius * 2,
            radius * 2,  # Width, height
            pen,
        )

        self.markers[(x, y)] = circle

        return circle

    def remove_star_marker(self, x: float, y: float):
        """Remove a circular marker at image coordinates x, y"""
        logging.debug(f"Removing marker at position ({x:.1f},{y:.1f})")

        if (x, y) in self.markers:
            marker = self.markers.pop((x, y))
            self.scene().removeItem(marker)

    def clear_markers(self):
        """Remove all star markers"""
        for coordinate, _ in self.markers:
            self.remove_star_marker(*coordinate)

    def display_image(self, image: FITSImage):
        """Display given FITS data array"""

        self.clear_markers()

        transform = None
        if self.current_image is not None:
            transform = self.transform()

        # Store new image
        self.current_image = image

        # Get normalized information
        display_data = image.get_normalized_data()

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
        if transform:
            self.setTransform(transform)

        self.display_markers_for_image(image)

    def clear_image(self):
        """Clear current image from view"""
        self.current_image = None
        self.clear_markers()
        self.pixmap_item.setPixmap(QPixmap())

    def display_markers_for_image(self, image):
        """Restore markers from image state"""
        # Add markers from image

        if image.target_star_idx is not None:
            star = image.get_star(image.target_star_idx)
            if star is not None:
                self.add_star_marker(star.x, star.y, colour="cyan")

        for idx in image.reference_star_idxs:
            star = image.get_star(idx)
            if star is not None:
                self.add_star_marker(star.x, star.y, colour="magenta")

    def update_display(self):
        if self.current_image is None:
            return

        self.display_image(self.current_image)

    @Slot(int)
    def set_brightness(self, value: int):
        """Set the brightness of the current image"""
        if self.current_image is None:
            return

        self.current_image.brightness_offset = value
        self.update_display()

    @Slot(int)
    def set_contrast(self, value: int):
        """Set the contrast of the current image"""
        if self.current_image is None:
            return

        self.current_image.contrast_factor = value / 100  # Normalize to ~1
        self.update_display()
