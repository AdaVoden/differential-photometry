from abc import ABC, abstractmethod

import numpy as np


class BaseStretch(ABC):
    """Interface for all stretch types"""

    @abstractmethod
    def build_lut(self, low: float, high: float) -> np.ndarray:
        """Return a LUT: a (256,) uint8 array mapping input -> output"""
        ...
