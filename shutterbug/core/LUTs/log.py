import numpy as np
from .base_stretch import BaseStretch
from .registry import register_stretch


@register_stretch("log")
class LogStretch(BaseStretch):
    def build_lut(self, low: float, high: float) -> np.ndarray:
        if high <= low:
            return np.arange(256, dtype=np.uint8)

        x = np.linspace(0, 1, 256)
        norm = np.clip((x - low) / (high - low), 0, 1)

        # Add epsilon to avoid log(0)
        # eps = 1e-6
        y = np.log1p(norm * 100) / np.log1p(100)

        return y
