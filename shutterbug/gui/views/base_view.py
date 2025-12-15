from typing import List
from PySide6.QtGui import QAction, QIcon

from shutterbug.gui.base_ui_widget import BaseUIWidget


class BaseView(BaseUIWidget):
    name: str
    icon: QIcon

    def create_header_actions(self) -> List[QAction]:
        """Returns actions in for use in menus"""
        return []
