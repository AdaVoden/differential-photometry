from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from shutterbug.core.app_controller import AppController

from PySide6.QtGui import QIcon, QTransform

from shutterbug.core.managers.base_manager import BaseManager


class IconManager(BaseManager):
    def __init__(self, controller: AppController):
        base = controller.resources / "icons"

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
