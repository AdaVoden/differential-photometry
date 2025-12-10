from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from shutterbug.core.app_controller import AppController

from shutterbug.gui.operators.base_operator import BaseOperator
from shutterbug.gui.panels.base_popover import BasePopOver
from shutterbug.gui.panels.collapsible_section import CollapsibleSection


class OperatorPanel(BasePopOver):

    def __init__(self, controller: AppController, parent):
        super().__init__(controller, parent)
        # Initially hidden
        self.hide()

    def set_panel(self, operator: BaseOperator):
        layout = self.layout()
        if layout is None:
            return

        # Remove all other widgets
        while layout.count():
            item = layout.takeAt(0)
            if w := item.widget():
                w.deleteLater()

        # Add new!
        settings = operator.create_settings_widget()
        if settings is not None:
            section = CollapsibleSection(
                settings.name, [settings], self.controller, self
            )
            layout.addWidget(section)

    def show_at_corner(self):
        """Shows popover panel at bottom left corner"""
        if self.parent():
            self.adjustSize()
            # From left, from top
            self.move(10, self.parent().height() - self.height() - 10)
        self.show()
