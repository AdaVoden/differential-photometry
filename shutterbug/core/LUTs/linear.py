import numpy as np
from .base_stretch import BaseStretch
from .registry import register_stretch


@register_stretch("linear")
class LinearStretch(BaseStretch):
    def build_lut(self, low: float, high: float) -> np.ndarray:
        # Avoid division by 0
        if high <= low:
            return np.arange(256)

        # Normalize input range to 0-1
        x = np.linspace(0, 1, 256)
        y = np.clip((x - low) / (high - low), 0, 1)

        return y
