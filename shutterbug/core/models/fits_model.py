from pathlib import Path
from uuid import uuid4

from math import floor, ceil

from .base_observable import ObservableQObject

import numpy as np


class FITSModel(ObservableQObject):
    """FITS image data and display class"""

    # Display defaults
    BRIGHTNESS_OFFSET_DEFAULT = 0
    CONTRAST_FACTOR_DEFAULT = 1
    STAMP_PADDING_DEFAULT = 50

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
        self.data_min = 0.0
        self.data_max = 0.0

        self.p_min = 0
        self.p_max = 0

        self.histogram = np.array([])
        self.bin_edges = np.array([])

        # Stamp variables
        self.stamp_padding = self.STAMP_PADDING_DEFAULT

        # Image display settings
        self.brightness: int = self._define_field(
            "brightness", self.BRIGHTNESS_OFFSET_DEFAULT
        )
        self.contrast: int = self._define_field(
            "contrast", self.CONTRAST_FACTOR_DEFAULT
        )

        # Star variables, computed
        self.background: float | None = None

    def get_stamp(self, x: float, y: float, r: float):
        """Gets selected stamp of main data image"""
        r = r + self.stamp_padding
        x0, x1 = floor(x - r), ceil(x + r)
        y0, y1 = floor(y - r), ceil(y + r)
        data = self.data[y0:y1, x0:x1]
        data = self.bzero + data * self.bscale
        return data

    def get_stamp_from_points(self, x0: int, x1: int, y0: int, y1: int):
        data = self.data[y0:y1, x0:x1]
        return self.bzero + data * self.bscale
