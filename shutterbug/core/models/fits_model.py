from pathlib import Path
from uuid import uuid4

from .base_observable import ObservableQObject


class FITSModel(ObservableQObject):
    """FITS image data and display class"""

    # Display defaults
    BRIGHTNESS_OFFSET_DEFAULT = 0
    CONTRAST_FACTOR_DEFAULT = 1

    def __init__(
        self, filepath: Path, data, obs_time: str, bzero: float, bscale: float
    ) -> None:
        super().__init__()
        self.uid = uuid4().hex
        # File data
        self.filepath: Path = filepath
        self.filename: str = self.filepath.name
        self.observation_time: float = float(obs_time)
        self.data = data

        # Image scaling
        self.bzero = bzero
        self.bscale = bscale

        # Data for display
        self.display_data = None

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

    def get_stamp(self, x: float, y: float, r: float):
        """Gets selected stamp of main data image"""
        x0, x1 = x - r, x + r
        y0, y1 = y - r, y + r
        return self.data[y0:y1, x0:x1]
