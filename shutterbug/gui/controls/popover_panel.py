from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QButtonGroup, QToolButton, QVBoxLayout, QWidget
from shutterbug.gui.tools import Tool, SelectTool, BoxSelectTool, AbstractTool


class PopOverPanel(QWidget):
    closed = Signal()
    tool_selected = Signal(Tool)

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

        # Button creation
        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)

        self.select_btn = self._make_button("Select", SelectTool, checked=True)
        self.box_btn = self._make_button("Box Select", BoxSelectTool)

        layout.addWidget(self.select_btn)
        layout.addWidget(self.box_btn)

    def _make_button(self, text: str, tool: AbstractTool, checked=False) -> QToolButton:
        """Makes a toggle-able button"""
        btn = QToolButton()
        btn.setText(text)
        btn.setCheckable(True)
        btn.setChecked(checked)
        btn.clicked.connect(lambda checked, b=btn: self.tool_selected.emit(tool))
        btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)

        # register in exclusive group
        self.button_group.addButton(btn)

        return btn

    def show_at_corner(self):
        """Shows popover panel at upper left corner"""
        if self.parent():
            self.adjustSize()
            # From left, from top
            self.move(10, 10)
        self.show()
