from PySide6.QtWidgets import QPushButton, QVBoxLayout, QWidget
from typing import List


class CollapsibleSection(QWidget):
    def __init__(self, title: str, content: List[QWidget], parent=None):
        super().__init__(parent)

        self.content = content
        self.is_expanded = True

        # Layout setup
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        self.header = QPushButton(title)
        self.header.setCheckable(True)
        self.header.setChecked(True)
        self.header.clicked.connect(self.toggle)

        layout.addWidget(self.header)
        for widget in content:
            layout.addWidget(widget)

    def toggle(self):
        self.is_expanded = not self.is_expanded
        for widget in self.content:
            widget.setVisible(self.is_expanded)
            self.header.setChecked(self.is_expanded)
