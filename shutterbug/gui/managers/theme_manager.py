from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from shutterbug.core.app_controller import AppController

from jinja2 import Template

from shutterbug.core.managers.base_manager import BaseManager


class ThemeManager(BaseManager):

    def __init__(self, controller: AppController, parent=None):
        super().__init__(controller, parent)
        self.colours = self.load_colours()
        self.qss_template = self.load_template()

    def apply_theme(self):
        """Applies currently selected theme"""
        pass

    def load_template(self):
        """Loads jinja2 template"""
        pass

    def load_colours(self):
        """Loads colours into system"""
        pass
