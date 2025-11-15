from pathlib import Path

from .base_observable import ObservableQObject

import numpy as np


class FITSModel(ObservableQObject):
    """FITS image data and display class"""

    # Display defaults
    BRIGHTNESS_OFFSET_DEFAULT = 0
    CONTRAST_FACTOR_DEFAULT = 1

    def __init__(
        self, filepath: Path, data, obs_time: str, bzero: float, bscale: float
    ) -> None:
        super().__init__()
        # File data
        self.filepath: Path = filepath
        self.filename: str = self.filepath.name
        self.observation_time: float = float(obs_time)
        self.data = data

        # Image scaling
        self.bzero = bzero
        self.bscale = bscale

        # Data for display
        self.display_data = self._compute_8bit_preview()

        # Image display settings
        self.brightness: int = self._define_field(
            "brightness", self.BRIGHTNESS_OFFSET_DEFAULT
        )
        self.contrast: int = self._define_field(
            "contrast", self.CONTRAST_FACTOR_DEFAULT
        )

        # Star variables, computed
        self.background: float | None = None
        self.stars = None  # Detected stars

    def _compute_8bit_preview(self):
        """Computes the 8 bit display image from the data"""

        # Get and scale data appropriately
        data = self.bzero + (self.data * self.bscale)

        # Handle NaNs and Infs
        data = np.nan_to_num(data, nan=0.0, posinf=0.0, neginf=0.0)

        # Simple fixed percentiel stretch
        vmin, vmax = np.percentile(data, [1, 99])

        # clip and normalize to 0-1
        data = np.clip(data, vmin, vmax)
        data = (data - vmin) / (vmax - vmin)

        # clip and convert to 0-255
        data = np.clip(data, 0, 1)
        data = (data * 255).astype(np.uint8)

        return data
