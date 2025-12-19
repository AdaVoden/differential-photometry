from __future__ import annotations

from typing import TYPE_CHECKING, Type

from PySide6.QtGui import QIcon


if TYPE_CHECKING:
    from shutterbug.core.app_controller import AppController

from PySide6.QtCore import QSize, Qt, Slot
from PySide6.QtWidgets import QButtonGroup, QToolButton, QWidget
from shutterbug.core.events import Event
from shutterbug.gui.panels.base_popover import BasePopOver
from shutterbug.gui.tools import BaseTool, BoxSelectTool, SelectTool, PhotometryTool


class ToolPanel(BasePopOver):

    def __init__(self, controller: AppController, parent: QWidget | None = None):
        super().__init__(controller, parent)

        # Button creation
        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        # get the icons
        select_icon = controller.icons.get("select")
        box_icon = controller.icons.get("box-select")
        phot_icon = controller.icons.get("photometry")

        self.select_btn = self._make_button(select_icon, SelectTool, checked=True)
        self.box_btn = self._make_button(box_icon, BoxSelectTool)
        self.phot_btn = self._make_button(phot_icon, PhotometryTool)

        layout = self.layout()

        # The things I do for typing
        if layout is not None:
            layout.addWidget(self.select_btn)
            layout.addWidget(self.box_btn)
            layout.addWidget(self.phot_btn)

        tool = self.controller.selections.tool
        if tool:
            self._select_button(tool.name)

        self.subscribe("tool.selected", self._on_tool_selected)

    def _select_button(self, name: str):
        """Selects appropriate button from selected tool"""
        if name == "Select":
            self.select_btn.setChecked(True)
        elif name == "Box Select":
            self.box_btn.setChecked(True)
        elif name == "Photometry":
            self.phot_btn.setChecked(True)
        else:
            self.select_btn.setChecked(False)
            self.box_btn.setChecked(False)
            self.phot_btn.setChecked(False)

    @Slot(Event)
    def _on_tool_selected(self, event: Event):
        """Handles tool being selected"""
        tool = event.data
        if tool:
            self._select_button(tool.name)

    def _make_button(
        self, icon: QIcon, tool: Type[BaseTool], checked=False
    ) -> QToolButton:
        """Makes a toggle-able button"""
        btn = QToolButton()
        btn.setIcon(icon)
        btn.setIconSize(QSize(32, 32))
        btn.setCheckable(True)
        btn.setChecked(checked)
        btn.clicked.connect(lambda: self.controller.tools.set_tool(tool))
        btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)

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
