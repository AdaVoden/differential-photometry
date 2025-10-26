import logging

from PySide6.QtWidgets import QGraphicsView, QGraphicsScene
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QPixmap, QImage

from shutterbug.gui.image_data import FITSImage

import numpy as np


class Viewer(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.current_image: FITSImage | None = None
        # Initial variables
        self.zoom_factor = 1.1

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
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

        # Set initial zoom level
        self.scale(1.0, 1.0)

        logging.debug("Viewer initialized")

    def wheelEvent(self, event):

        if event.angleDelta().y() > 0:  # Zoom in
            self.scale(self.zoom_factor, self.zoom_factor)
        else:  # Zoom out
            self.scale(1 / self.zoom_factor, 1 / self.zoom_factor)
        event.accept()

        super().wheelEvent(event)  # Pass other wheel events to parent

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
        if self.current_image is None:
            return
        self.current_image.brightness_offset = value
        self.update_display()

    @Slot(int)
    def set_contrast(self, value: int):
        if self.current_image is None:
            return
        
        self.current_image.contrast_factor = value / 100  # Normalize to ~1
        self.update_display()
