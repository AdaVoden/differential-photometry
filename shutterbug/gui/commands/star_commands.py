from PySide6.QtGui import QUndoCommand

from shutterbug.gui.image_data import FITSImage

from shutterbug.gui.stars import StarMeasurement


class SelectStarCommand(QUndoCommand):
    """Command to select a star"""

    def __init__(self, star, image: FITSImage):
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
        self.star_manager.catalog.register_measurement(self.measurement)

    def undo(self):
        self.star_manager.remove_star(self.measurement)
        self.star_manager.catalog.unregister_measurement(self.measurement)


class DeselectStarCommand(QUndoCommand):
    """Command to deselect a star"""

    def __init__(self, star, image: FITSImage):
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
        self.star_manager.catalog.unregister_measurement(self.measurement)

    def undo(self):
        self.star_manager.add_star(self.measurement)
        self.star_manager.catalog.register_measurement(self.measurement)
