from PySide6.QtGui import QUndoCommand

from shutterbug.gui.viewer import Viewer
from shutterbug.gui.outliner import Outliner
from shutterbug.gui.main_window import MainWindow
from shutterbug.gui.image_data import FITSImage

from astropy.io import fits

from pathlib import Path

from typing import List

import logging

def load_fits_image(filepath: Path):
    """Load FITS image from given filepath"""
    # This method can be implemented to load FITS data
    logging.debug(f"Loading FITS image from {filepath}")

    with fits.open(filepath) as hdul:
        data = hdul[0].data  # type: ignore
        obs_time = hdul[0].header["JD"]  # type: ignore
        image = FITSImage(filepath, data, obs_time)
        # Assuming image data is in the primary HDU
        return image

def load_images(image_paths: List[Path], main_window: MainWindow, viewer: Viewer, outliner: Outliner):
    """Batch loads FITS images from list of paths"""
    for path in image_paths:
        # Load it into outliner and main window first
        image = load_fits_image(path)
        outliner.add_item(image.filename)
        main_window.fits_data[image.filename] = image
    # Load first image in list into viewer
    # And select in outliner        
    first = image_paths[0]
    viewer.display_image(main_window.fits_data[first.name])
    outliner.select_item(first.name)
        
def remove_images(image_names: List[Path], main_window: MainWindow, viewer: Viewer, outliner: Outliner):
    """Batch remove FITS images from application"""
    for image in image_names:
        name = image.name

        # Remove from main window and image
        image = main_window.fits_data.pop(name)
        if viewer.current_image == image:
            viewer.clear_image()
        
        # Remove from outliner
        item = outliner.get_item(name)
        if item:
            outliner.remove_item(item)


class LoadImagesCommand(QUndoCommand):
    """Loads images into application"""
    def __init__(self, image_paths: List[str], main_window: MainWindow, viewer: Viewer, outliner: Outliner):
        self.image_paths = [Path(f) for f in image_paths]
        self.viewer = viewer
        self.outliner = outliner
        self.main_window = main_window

    def redo(self) -> None:
        logging.debug(f"Load images command activated for {len(self.image_paths)} images")
        load_images(image_paths = self.image_paths,
                    main_window=self.main_window,
                    viewer=self.viewer,
                    outliner=self.outliner)

    def undo(self) -> None:
        logging.debug(f"Undoing image load of {len(self.image_paths)} images")
        remove_images(image_names=self.image_paths,
                      main_window=self.main_window,
                      viewer=self.viewer,
                      outliner=self.outliner)

class RemoveImagesCommand(QUndoCommand):
    """Removes image from application"""
    def __init__(self, image_paths: Path):
        self.image_paths = image_paths

    def redo(self) -> None:
        pass

    def undo(self) -> None:
        pass
    
class FileSelectedCommand(QUndoCommand):
    """Selects file in outliner and viewer"""
    def __init__(self):
        pass

    def redo(self) -> None:
        pass

    def undo(self) -> None:
        pass
