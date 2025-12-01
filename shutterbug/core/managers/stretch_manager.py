from typing import Optional
from PySide6.QtCore import QObject, Signal
from shutterbug.core.LUTs import get_stretch, BaseStretch
import numpy as np

import logging


class StretchManager(QObject):
    lut_changed = Signal()

    def __init__(self):
        super().__init__()
        self.lut = np.arange(256, dtype=np.uint8)
        self.brightness = 0
        self.contrast = 1.0
        self.low_p = 0.005
        self.high_p = 0.995
        self.stretch: Optional[BaseStretch] = None

    def update_lut(self):
        """Updates lookup table for display"""
        if self.stretch is None:
            logging.error("No stretch detected")
            return np.arange(256)  # No stretch
        y = self.stretch.build_lut(self.low_p, self.high_p)

        y = y * self.contrast + self.brightness
        y = np.clip(y * 255, 0, 255).astype(np.uint8)

        self.lut = y
        self.lut_changed.emit()

    def apply(self, display_data):
        """Apply LUT to display data"""
        return self.lut[display_data]

    def set_mode(self, mode: str):
        """Sets stretch mode"""
        logging.debug(f"Setting stretch to: {mode}")
        self.stretch = get_stretch(mode)
        if self.stretch is None:
            logging.error(f"No stretch {mode} found")
        self.update_lut()
