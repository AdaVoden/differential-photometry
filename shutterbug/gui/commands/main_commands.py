from PySide6.QtGui import QUndoCommand

from pathlib import Path


class LoadImagesCommand(QUndoCommand):
    def __init__(self, image_paths: Path):
        self.image_paths = image_paths

    def redo(self) -> None:
        pass

    def undo(self) -> None:
        pass


class RemoveImagesCommand(QUndoCommand):
    def __init__(self, image_paths: Path):
        self.image_paths = image_paths

    def redo(self) -> None:
        pass

    def undo(self) -> None:
        pass
