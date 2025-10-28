import logging

from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QMenu
from PySide6.QtCore import Qt, Slot, QPoint, Signal
from PySide6.QtGui import QContextMenuEvent, QPixmap, QImage, QPen, QColor, QMouseEvent

from shutterbug.gui.image_data import FITSImage, SelectedStar

from typing import Tuple

import numpy as np


class Viewer(QGraphicsView):

    clicked = Signal(QMouseEvent)
    find_stars_requested = Signal()
    photometry_requested = Signal()

    def __init__(self):
        super().__init__()
        # Initial variables
        self.current_image: FITSImage | None = None
        self.target_marker = None  # Target star marker
        self.reference_markers = []  # Reference star markers
        # Zoom variables
        self.zoom_factor: float = 1.1
        self.zoom_max: float = 5.0
        self.zoom_min: float = 0.1
        self.scale(1.0, 1.0)

        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("background-color: black;")

        # Set up scene
        scene = QGraphicsScene(self)
        self.setScene(scene)

        # Add pixmap item to scene, blank for now
        self.pixmap_item = scene.addPixmap(QPixmap())

        # Set up panning and scrolling
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        # Scrollbars look ugly here
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Set up zooming behavior
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        # TODO Fix issue where zoom is not under cursor

        logging.debug("Viewer initialized")

    def wheelEvent(self, event):
        # M11 is the horizontal scaling factor
        current_scale = self.transform().m11()
        if event.angleDelta().y() > 0:  # Zoom in
            if current_scale * self.zoom_factor <= self.zoom_max:
                self.scale(self.zoom_factor, self.zoom_factor)
        else:  # Zoom out
            if current_scale * self.zoom_factor >= self.zoom_min:
                self.scale(1 / self.zoom_factor, 1 / self.zoom_factor)
        event.accept()

        super().wheelEvent(event)  # Pass other wheel events to parent

    def mousePressEvent(self, event: QMouseEvent):
        self.clicked.emit(event)
        super().mousePressEvent(event)

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        menu = QMenu()

        # select_star_action = menu.addAction("Select as Target Star")

        find_stars_action = menu.addAction("Find all stars in image")
        find_stars_action.triggered.connect(self.find_stars_requested)

        calc_phot_action = menu.addAction("Calculate magnitude for selected star")
        calc_phot_action.triggered.connect(self.photometry_requested)
        # TODO add in "Select as Reference Star" "Set Aperture", etc.

        menu.exec(event.globalPos())

        super().contextMenuEvent(event)

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
        radius: int = 20,
        colour: str = "cyan",
        reference: bool = False,
    ):
        """Add a circular marker at image coordinates x, y"""

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
        if reference:
            self.reference_markers.append(circle)
        else:
            if self.target_marker is not None:
                self.scene().removeItem(self.target_marker)
            self.target_marker = circle

        return circle

    def clear_markers(self):
        """Remove all star markers"""
        for marker in self.reference_markers:
            self.scene().removeItem(marker)
        self.reference_markers.clear()

        if self.target_marker:
            self.scene().removeItem(self.target_marker)
            self.target_marker = None

    def display_image(self, image: FITSImage):
        """Display given FITS data array"""

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
