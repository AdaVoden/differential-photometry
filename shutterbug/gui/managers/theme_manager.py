from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from shutterbug.core.app_controller import AppController

from PySide6.QtWidgets import QApplication
from jinja2 import Template
import yaml

from shutterbug.core.managers.base_manager import BaseManager


class ThemeManager(BaseManager):
    stylesheets = [
        "base.qss",
        "controls.qss",
        "panels.qss",
    ]

    def __init__(self, controller: AppController, parent=None):
        super().__init__(controller, parent)
        self.base = controller.resources
        self.themes_dir = self.base / "themes"
        self.qss_dir = self.base / "qss"
        self.current = "gruvbox-dark"

        self._colours = self.load_colours()
        self._qss_template = self.load_template()

    def apply_theme(self):
        """Applies currently selected theme"""
        qss = self._qss_template.render(**self._colours)
        app = QApplication.instance()
        if app:
            app.setStyleSheet(qss)  # type: ignore

    def load_template(self):
        """Loads jinja2 template"""
        sheets = self._load_stylesheets()

        return Template(sheets)

    def load_colours(self):
        """Loads colours into system"""
        with open(self.themes_dir / f"{self.current}.yaml", "r") as f:
            colours = yaml.safe_load(f)

        return colours

    def _load_stylesheets(self):
        combined = ""
        for sheet in self.stylesheets:
            with open(self.qss_dir / sheet, "r") as f:
                combined += f.read() + "\n"

        return combined

    @property
    def colours(self):
        return self._colours
