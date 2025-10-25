import logging

from PySide6.QtWidgets import QGraphicsView, QGraphicsScene
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QPixmap, QImage

import numpy as np


class Viewer(QGraphicsView):
    def __init__(self):
        super().__init__()
        # Initial variables
        self.brightness_offset = 0
        self.contrast_factor = 1.0
        self.original_data = None # Original FITS data
        self.data = None # Display data
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
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Set up zooming behavior
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

        # Set initial zoom level
        self.scale(1.0, 1.0)

        logging.debug("Viewer initialized")

    def wheelEvent(self, event):
        if (
            event.modifiers() == Qt.KeyboardModifier.ControlModifier
        ):  # Zoom only when Ctrl is pressed
            if event.angleDelta().y() > 0:  # Zoom in
                self.scale(self.zoom_factor, self.zoom_factor)
            else:  # Zoom out
                self.scale(1 / self.zoom_factor, 1 / self.zoom_factor)
            event.accept()
        else:
            super().wheelEvent(event)  # Pass other wheel events to parent

    def display_image(self, data):
        """Display given FITS data array"""
        
        # Store original data if this is first load
        if self.original_data is None or data is not self.original_data:
            self.original_data = data.copy()
        
        # Normalize with current brightness/contrast
        display_data = self.normalize_data(data)
        self.data = display_data

        # Convert to QImage
        height, width = display_data.shape
        qimage = QImage(display_data.data, width, height, QImage.Format.Format_Grayscale8)

        # Display
        pixmap = QPixmap.fromImage(qimage)
        self.pixmap_item.setPixmap(pixmap)
        self.fitInView(self.pixmap_item, Qt.AspectRatioMode.KeepAspectRatio)

    def normalize_data(self, data):
        """Normalize the FITS data to 0-255 for display"""

       # Handle NaNs and Infs
        data = np.nan_to_num(data, nan=0.0, posinf=0.0, neginf=0.0)
        
        # Simple fixed percentile stretch
        vmin, vmax = np.percentile(data, [1, 99])
        
        # Clip and normalize to 0-1 first
        data = np.clip(data, vmin, vmax)
        data = (data - vmin) / (vmax - vmin + 1e-10)  # Avoid divide by zero
        
        # apply contrast and brightness to 0-1 range
        # Contrast: multiply (1.0 = no change)
        data = data * self.contrast_factor
        
        # Brightness: add/subtract (-1 to 1 range)
        data = data + (self.brightness_offset / 100.0)
        
        # Clip to 0-1 and convert to 0-255
        data = np.clip(data, 0, 1)
        data = (data * 255).astype(np.uint8)

        return data

    def update_display(self):
        if self.original_data is None:
            return

        self.display_image(self.original_data)

    @Slot(int)
    def set_brightness(self, value):
        self.brightness_offset = value
        self.update_display()

    @Slot(int)
    def set_contrast(self, value):
        self.contrast_factor = value / 100  # Normalize to ~1
        self.update_display()
