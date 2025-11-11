from pathlib import Path

from .base_observable import ObservableQObject


class FITSModel(ObservableQObject):
    """FITS image data and display class"""

    # Display defaults
    BRIGHTNESS_OFFSET_DEFAULT = 0
    CONTRAST_FACTOR_DEFAULT = 100

    def __init__(self, filepath: Path, data, obs_time: str) -> None:
        super().__init__()
        # File data
        self.filepath: Path = filepath
        self.filename: str = self.filepath.name
        self.observation_time: float = float(obs_time)
        self.data = data

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
