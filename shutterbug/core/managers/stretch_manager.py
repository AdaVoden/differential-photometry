from PySide6.QtCore import QObject, Signal

import numpy as np


class StretchManager(QObject):
    lut_changed = Signal()

    def __init__(self):
        super().__init__()
        self.lut = np.arange(256, dtype=np.uint8)
        self.brightness = 0
        self.contrast = 1.0

    def update_lut(self):
        """Updates lookup table for display"""
        # Linear stretch
        x = np.arange(256)
        y = x * self.contrast + self.brightness
        y = np.clip(y, 0, 255).astype(np.uint8)

        self.lut = y
        self.lut_changed.emit()

    def apply(self, display_data):
        """Apply LUT to display data"""
        return self.lut[display_data]

    def set_mode(self, mode: str):
        """Sets stretch mode"""
        pass
