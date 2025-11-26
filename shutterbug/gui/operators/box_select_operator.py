from PySide6.QtCore import QRect, QSize
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QRubberBand
from shutterbug.gui.commands.star_commands import AddMeasurementsCommand
from shutterbug.gui.operators.base_operator import BaseOperator


class BoxSelectOperator(BaseOperator):
    def start(self, event: QMouseEvent):
        """Begins selection box at point of click"""
        self.start_pos = event.pos()
        self.rubber = QRubberBand(QRubberBand.Shape.Rectangle, self.viewer)
        self.rubber.setGeometry(QRect(event.pos(), QSize()))
        self.rubber.show()

    def update(self, event: QMouseEvent):
        """Updates selection box on mouse move"""
        if not self.active:
            return
        end_pos = event.pos()
        rect = QRect(self.start_pos, end_pos).normalized()
        self.rubber.setGeometry(rect)

    def build_command(self):
        scene_rect = self.viewer.viewport_rect_to_scene(self.rubber.geometry())
        stars = self._find_stars_in(scene_rect)
        if not stars:
            return None
        if not self.viewer.current_image:
            return None
        return AddMeasurementsCommand(stars, self.viewer.current_image)

    def cleanup_preview(self):
        self.rubber.deleteLater()

    def _find_stars_in(self, scene_rect: QRect):
        pass
