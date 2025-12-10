from pathlib import Path

from PySide6.QtGui import QIcon, QTransform


class IconManager:
    def __init__(self):
        base = Path(__file__).resolve().parent.parent.parent / "resources" / "icons"

        self._icons = {f.stem: QIcon(str(f)) for f in base.glob("*.svg")}

    def get(self, name: str):
        """Returns named icon, if it exists"""
        return self._icons.get(name) or QIcon()

    def get_rotated(self, name: str, degrees: int):
        """Gets icon but rotated a specific number of degrees"""
        icon = self._icons.get(name)
        if icon is None:
            return QIcon()

        pixmap = icon.pixmap(24, 24)
        transform = QTransform().rotate(degrees)
        rotated = pixmap.transformed(transform)
        return QIcon(rotated)
