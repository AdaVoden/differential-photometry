from PySide6.QtGui import QUndoCommand

from shutterbug.gui.image_data import FITSImage

from shutterbug.gui.stars import StarMeasurement


class SelectStarCommand(QUndoCommand):
    """Command to select a star"""

    def __init__(self, star, image: FITSImage, is_reference: bool):
        super().__init__()
        self.star = star
        self.image = image
        self.star_manager = image.star_manager
        self.is_reference = is_reference

    def redo(self):
        measurement = StarMeasurement(
            self.star["xcentroid"], self.star["ycentroid"], self.star["flux"]
        )
        self.star_manager.add_star(measurement)

    def undo(self):
        measurement = self.star_manager.find_nearest(
            star["xcentroid"], star["ycentroid"]
        )
        self.star_manager.remove_star(measurement)


class DeselectStarCommand(QUndoCommand):
    """Command to deselect a star"""

    def __init__(self):
        super().__init__()

    def redo(self):
        pass

    def undo(self):
        pass
