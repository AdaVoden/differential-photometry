from PySide6.QtWidgets import QWidget, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QImage

from astropy.io import fits
import numpy as np


class Viewer(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("background-color: black;")
        self.setText("No Image Loaded")

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
        self.setPixmap(
            pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )

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
