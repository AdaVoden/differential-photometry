from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QVBoxLayout, QWidget


class BasePopOver(QWidget):
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
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

    def show_at_corner(self):
        pass
