from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget


class LabeledWidget(QWidget):
    """Reusable labeled widget"""

    def __init__(self, label: str):
        super().__init__()
        layout = QHBoxLayout()
        self.setLayout(layout)

        # Set up margins and spacing
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        layout.addStretch(1)

        # QLabel for display
        self.label = QLabel(label)
        self.label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        layout.addWidget(self.label)
