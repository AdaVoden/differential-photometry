from PySide6.QtCore import Qt
from PySide6.QtGui import QMouseEvent, QUndoCommand
from shutterbug.gui.operators.base_operator import BaseOperator


class SelectOperator(BaseOperator):

    def start(self, event: QMouseEvent):
        if event.modifiers() == Qt.KeyboardModifier.AltModifier:
            self.viewer.deselect_star(event.pos())

        self.viewer.select_star(event.pos())

    def build_command(self) -> QUndoCommand | None:
        pass
