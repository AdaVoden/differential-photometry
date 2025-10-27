import logging

from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QMenu
from PySide6.QtCore import Qt, Slot, QPoint
from PySide6.QtGui import QContextMenuEvent, QPixmap, QImage, QPen, QColor

from shutterbug.gui.image_data import FITSImage

from typing import Tuple

import numpy as np


class Viewer(QGraphicsView):
    def __init__(self):
        super().__init__()
        # Initial variables
        self.current_image: FITSImage | None = None
        self.star_markers = []  # store all markers for removal
        self.zoom_factor: float = 1.1

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
        # TODO Fix issue where zoom is not under cursor
        # TODO set max zoom limits

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

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.select_star_at_position(event.pos())

        super().mousePressEvent(event)

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        menu = QMenu()

        select_star_action = menu.addAction("Select as Target Star")
        select_star_action.triggered.connect(
            lambda: self.select_star_at_position(event.pos())
        )

        find_stars_action = menu.addAction("Find all stars in image")
        find_stars_action.triggered.connect(self.find_stars_in_image)

        # TODO add in "Select as Reference Star" "Set Aperture", etc.

        menu.exec(event.globalPos())

        super().contextMenuEvent(event)

    @Slot()
    def select_star_at_position(self, coordinates: QPoint):
        if self.current_image is None:
            return

        if self.current_image.stars is None:
            return

        x, y = self.convert_to_image_coordinates(coordinates)
        
        nearest_star = self.find_nearest_star(x, y)

        if nearest_star:
            # Place marker at actual star position
            star_x = nearest_star['xcentroid']
            star_y = nearest_star['ycentroid']
            self.clear_markers()
            self.add_star_marker(star_x, star_y)
            logging.info(f"Selected star at ({star_x:.1f}, {star_y:.1f})")
            # TODO Emit signal that star is selected
        else:
            logging.info(f"No star found near flick at ({x:.1f}, {y:.1f})")
        
        # TODO send star information to main window

    def find_nearest_star(self, x: float, y: float, max_distance: int = 20):
        if self.current_image is None:
            return

        if self.current_image.stars is None:
            return
        
        stars = self.current_image.stars

        # Calculate distance to all stars
        # TODO Make more efficient. Ktrees?
        distances = np.sqrt(
            (stars['xcentroid'] - x)**2 +
            (stars['ycentroid'] - y)**2
        )

        min_idx = np.argmin(distances)

        if distances[min_idx] <= max_distance:
            return stars[min_idx]
        
        return None



    def convert_to_image_coordinates(self, coordinate: QPoint) -> Tuple[float, float]:
        # Step 1, convert to scene coordinates
        scene_pos = self.mapToScene(coordinate)

        # Step 2, map to Pixmap
        pix_pos = self.pixmap_item.mapToScene(scene_pos)

        # Step 3, there is no step 3
        return pix_pos.x(), pix_pos.y()

    def add_star_marker(
        self, x: float, y: float, radius: int = 20, colour: str = "cyan"
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

        self.star_markers.append(circle)
        return circle

    def clear_markers(self):
        """Remove all star markers"""
        for marker in self.star_markers:
            self.scene().removeItem(marker)
        self.star_markers.clear()

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

    @Slot()
    def find_stars_in_image(self):
        if self.current_image is None:
            return

        self.current_image.find_stars()
        # TODO: Display stars on image, when hovered?
