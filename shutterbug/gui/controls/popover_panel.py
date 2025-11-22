from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class PopOverPanel(QWidget):
    closed = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        # Remove window frame
        self.setWindowFlags(Qt.WindowType.Widget | Qt.WindowType.FramelessWindowHint)
        # Allow translucent background, don't draw native one
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        # Styled our way not native way
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.setObjectName("popover")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        layout.addWidget(QLabel("Select"))
        layout.addWidget(QLabel("Box Select"))
        layout.addWidget(QLabel("Circle select"))

    def show_at_corner(self):
        """Shows popover panel at upper left corner"""
        if self.parent():
            self.adjustSize()
            # From left, from top
            self.move(12, 12)
        self.show()
