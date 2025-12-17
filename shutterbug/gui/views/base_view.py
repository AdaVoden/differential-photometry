from typing import List
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMenu, QWidget

from shutterbug.gui.base_ui_widget import BaseUIWidget


class BaseView(BaseUIWidget):
    name: str
    icon: QIcon

    def create_header_actions(self) -> List[QMenu | QWidget]:
        """Returns actions in for use in menus"""
        return []
