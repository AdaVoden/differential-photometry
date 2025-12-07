from __future__ import annotations

from typing import TYPE_CHECKING

from shutterbug.gui.operators.base_operator import BaseOperator

if TYPE_CHECKING:
    from shutterbug.gui.views.image import ImageViewer
    from shutterbug.core.app_controller import AppController

from PySide6.QtWidgets import QWidget


class BaseTool:
    name = "BaseTool"
    icon = None  # Optional

    def __init__(self) -> None:
        super().__init__()

    def create_operator(
        self, viewer: ImageViewer, controller: AppController
    ) -> BaseOperator:
        raise NotImplementedError

    def create_settings_widget(self) -> QWidget | None:
        return None
