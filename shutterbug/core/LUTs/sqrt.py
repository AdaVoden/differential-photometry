from shutterbug.core.LUTs.base_stretch import BaseStretch
from shutterbug.core.LUTs.registry import register_stretch

import numpy as np


@register_stretch("sqrt")
class SqrtStretch(BaseStretch):
    def build_lut(self, low: float, high: float) -> np.ndarray:
        if high <= low:
            return np.arange(256)

        x = np.linspace(0, 1, 256)
        norm = np.clip((x - low) / (high - low), 0, 1)

        y = np.sqrt(norm)

        return y
