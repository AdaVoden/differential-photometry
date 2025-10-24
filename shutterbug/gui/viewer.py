from PySide6.QtWidgets import QLabel, QGraphicsView, QGraphicsScene
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QPixmap, QImage

from astropy.io import fits
import numpy as np


class Viewer(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
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
        # Set zoom factor
        self.zoom_factor = 1.1

    def wheelEvent(self, event):
            if event.modifiers() == Qt.KeyboardModifier.ControlModifier: # Zoom only when Ctrl is pressed
                if event.angleDelta().y() > 0: # Zoom in
                    self.scale(self.zoom_factor, self.zoom_factor)
                else: # Zoom out
                    self.scale(1 / self.zoom_factor, 1 / self.zoom_factor)
                event.accept()
            else:
                super().wheelEvent(event) # Pass other wheel events to parent


    def load_fits_image(self, filename):
        """Load and display a FITS image from the given filename"""

        # Load fits file
        with fits.open(filename) as hdul:
            data = hdul[0].data  # Assuming image is in primary HDU

        # Normalize data for display
        data = self.normalize_data(data)

        # Convert to QImage
        height, width = data.shape
        qimage = QImage(data.data, width, height, QImage.Format.Format_Grayscale8)

        # Display
        pixmap = QPixmap.fromImage(qimage)
        self.pixmap_item.setPixmap(pixmap)
        self.fitInView(self.pixmap_item, Qt.AspectRatioMode.KeepAspectRatio)

        # Set up drag mode


        # Set up zooming (optional)



        # self.setPixmap(
        #     pixmap.scaled(
        #         self.size(),
        #         Qt.AspectRatioMode.KeepAspectRatio,
        #         Qt.TransformationMode.SmoothTransformation,
        #     )
        # )

    def normalize_data(self, data):
        """Normalize the FITS data to 0-255 for display"""

        # Handle NaNs and Infs
        data = np.nan_to_num(data, nan=0.0, posinf=0.0, neginf=0.0)

        # Clip to 1st and 99th percentiles
        vmin, vmax = np.percentile(data, [1, 99])
        data = np.clip(data, vmin, vmax)

        # Normalize to 0-255
        data = ((data - vmin) / (vmax - vmin) * 255.0).astype(np.uint8)

        return data
