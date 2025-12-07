from __future__ import annotations

from typing import TYPE_CHECKING

from shutterbug.gui.commands.select_commands import SelectCommand
from shutterbug.gui.commands.star_commands import AddMeasurementsCommand

if TYPE_CHECKING:
    from shutterbug.gui.views.image import ImageViewer
    from shutterbug.core.app_controller import AppController

from PySide6.QtGui import QMouseEvent, QUndoCommand
from shutterbug.gui.operators.base_operator import BaseOperator


class SelectOperator(BaseOperator):

    def __init__(self, viewer: ImageViewer, controller: AppController):
        super().__init__(viewer, controller)
        self.centroid = None
        self.image = self.viewer.current_image

    def start(self, event: QMouseEvent):
        self.cleanup_preview()
        self.centroid = self.viewer.get_centroid_at_point(event.pos())
        if self.centroid is not None:

            self.viewer.add_star_marker(
                self.centroid["xcentroid"], self.centroid["ycentroid"], colour="gold"
            )

    def create_settings_widget(self) -> None:
        return None

    def build_command(self) -> QUndoCommand | None:
        """Builds either a select or add command for target centroid"""

        if self.centroid is None or self.image is None:
            return None
        centroid = self.centroid
        star = self.controller.stars.find_nearest(
            centroid["xcentroid"], centroid["ycentroid"]
        )

        if star is None:
            cmd = AddMeasurementsCommand([centroid], self.image, self.controller)
        else:
            cmd = SelectCommand(star, self.controller)

        self.cleanup_preview()
        return cmd

    def cleanup_preview(self):
        """Clears the preview of the selection"""
        if self.centroid is not None:
            self.viewer.remove_star_marker(
                self.centroid["xcentroid"], self.centroid["ycentroid"]
            )
        self.centroid = None
