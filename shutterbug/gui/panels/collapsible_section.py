from __future__ import annotations

from typing import TYPE_CHECKING

from shutterbug.gui.base_ui_widget import BaseUIWidget

if TYPE_CHECKING:
    from shutterbug.core.app_controller import AppController


from PySide6.QtWidgets import QPushButton, QVBoxLayout, QWidget, QSizePolicy
from PySide6.QtCore import QSize, Qt
from typing import List


class CollapsibleSection(BaseUIWidget):
    def __init__(
        self,
        title: str,
        content: List[QWidget],
        controller: AppController,
        parent=None,
    ):
        super().__init__(controller, parent)
        # Initial variables
        self.content = content
        self.is_expanded = True
        self.title = title
        self.arrow = controller.icons.get_rotated("arrow-left", 180)
        self.arrow_down = controller.icons.get_rotated("arrow-left", -90)
        self.icon_size = QSize(24, 24)
        self.setObjectName("collapsibleSection")

        # Layout setup
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addStretch(1)

        # Sizing and alignment
        self.setSizePolicy(
            QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        )
        # Header
        self.header = QPushButton(f"{title}")
        self.header.setIcon(self.arrow_down)
        self.header.setIconSize(self.icon_size)
        self.header.setCheckable(True)
        self.header.setChecked(True)
        self.header.clicked.connect(self.toggle)
        self.header.setObjectName("header")

        # Content
        self.content_body = QWidget()
        self.content_body.setObjectName("collapsibleContentBody")
        content_layout = QVBoxLayout(self.content_body)
        self.content_layout = content_layout
        # Setup content layout
        content_layout.setContentsMargins(16, 8, 8, 8)
        content_layout.setSpacing(6)

        self.content_body.setLayout(content_layout)
        content_layout.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )

        layout.addWidget(self.header)
        layout.addWidget(self.content_body)
        for widget in content:
            content_layout.addWidget(widget)

    def toggle(self):
        self.is_expanded = not self.is_expanded
        for widget in self.content:
            widget.setVisible(self.is_expanded)
            self.header.setChecked(self.is_expanded)
        if self.is_expanded:
            self.header.setIcon(self.arrow_down)
            self.header.setIconSize(self.icon_size)
            self.content_layout.setContentsMargins(16, 8, 8, 8)

        else:
            self.header.setIcon(self.arrow)
            self.header.setIconSize(self.icon_size)
            self.content_layout.setContentsMargins(0, 0, 0, 0)
