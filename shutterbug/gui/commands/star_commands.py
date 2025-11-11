from PySide6.QtGui import QUndoCommand

from shutterbug.core.models import FITSModel, StarMeasurement


class SelectStarCommand(QUndoCommand):
    """Command to select a star"""

    def __init__(self, star, image: FITSModel):
        super().__init__()
        self.star = star
        self.image = image
        self.time = image.observation_time
        self.star_manager = image.star_manager
        self.measurement = StarMeasurement(
            x=self.star["xcentroid"],
            y=self.star["ycentroid"],
            time=self.time,
            image=self.image.filename,
        )

    def redo(self):
        self.star_manager.add_star(self.measurement)

    def undo(self):
        self.star_manager.remove_star(self.measurement)


class DeselectStarCommand(QUndoCommand):
    """Command to deselect a star"""

    def __init__(self, star, image: FITSModel):
        super().__init__()
        self.star = star
        self.image = image
        self.time = image.observation_time
        self.star_manager = image.star_manager
        self.measurement = StarMeasurement(
            x=self.star["xcentroid"],
            y=self.star["ycentroid"],
            time=self.time,
            image=self.image.filename,
        )

    def redo(self):
        self.star_manager.remove_star(self.measurement)

    def undo(self):
        self.star_manager.add_star(self.measurement)
