from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QButtonGroup, QToolButton, QWidget
from shutterbug.gui.panels.base_popover import BasePopOver
from shutterbug.gui.tools import BaseTool, BoxSelectTool, SelectTool, PhotometryTool


class ToolPanel(BasePopOver):
    tool_selected = Signal(BaseTool)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        # Button creation
        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)

        self.select_btn = self._make_button("Select", SelectTool, checked=True)
        self.box_btn = self._make_button("Box Select", BoxSelectTool)
        self.phot_btn = self._make_button("Photometry", PhotometryTool)

        layout = self.layout()

        # The things I do for typing
        if layout is not None:
            layout.addWidget(self.select_btn)
            layout.addWidget(self.box_btn)
            layout.addWidget(self.phot_btn)

    def _make_button(self, text: str, tool: BaseTool, checked=False) -> QToolButton:
        """Makes a toggle-able button"""
        btn = QToolButton()
        btn.setText(text)
        btn.setCheckable(True)
        btn.setChecked(checked)
        btn.clicked.connect(lambda: self.tool_selected.emit(tool))
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
