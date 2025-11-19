from PySide6.QtGui import QUndoCommand

from shutterbug.core.models import FITSModel
from shutterbug.core.managers import ImageManager, SelectionManager

from astropy.io import fits

from pathlib import Path

from typing import List

import logging


class LoadImagesCommand(QUndoCommand):
    """Loads images into application"""

    def __init__(
        self,
        image_paths: List[str],
        image_manager: ImageManager,
    ):
        super().__init__("Load Images")
        self.image_paths = [Path(f) for f in image_paths]
        self.image_manager = image_manager

    def redo(self) -> None:
        logging.debug(
            f"COMMAND: Load images command activated for {len(self.image_paths)} images"
        )
        load_images(self.image_paths, self.image_manager)

    def undo(self) -> None:
        logging.debug(f"COMMAND: Undoing image load of {len(self.image_paths)} images")
        remove_images(self.image_paths, self.image_manager)


class RemoveImagesCommand(QUndoCommand):
    """Removes image from application"""

    def __init__(self, image_names: List[str], image_manager: ImageManager):
        super().__init__("Remove Images")
        self.image_manager = image_manager
        images = []
        for name in image_names:
            image = image_manager.get_image(name)
            if image:
                images.append(image)
        image_paths = [i.filepath for i in images]
        self.image_paths = image_paths

    def redo(self) -> None:
        logging.debug(f"COMMAND: Removing {len(self.image_paths)} images from project")
        remove_images(
            self.image_paths,
            self.image_manager,
        )

    def undo(self) -> None:
        logging.debug(
            f"COMMAND: Undoing removal of {len(self.image_paths)} images from project"
        )
        load_images(
            self.image_paths,
            self.image_manager,
        )


class SelectFileCommand(QUndoCommand):
    """Selects file in outliner and viewer"""

    def __init__(self, selected_image: FITSModel):
        super().__init__("Select File")
        self.selected_image = selected_image
        self.selection_m = SelectionManager()
        self.old = self.selection_m._current

    def redo(self) -> None:
        logging.debug(
            f"COMMAND: Setting active image to: {self.selected_image.filename}"
        )
        self.selection_m.set_selected_object(self.selected_image)

    def undo(self) -> None:
        logging.debug(
            f"COMMAND: undoing setting active image to: {self.selected_image.filename}"
        )

        self.selection_m.set_selected_object(self.old)


def load_fits_image(filepath: Path):
    """Load FITS image from given filepath"""
    # This method can be implemented to load FITS data
    logging.debug(f"Loading FITS image from {filepath}")

    with fits.open(
        filepath, uint=True, memmap=True, do_not_scale_image_data=True
    ) as hdul:
        data = hdul[0].data  # type: ignore
        obs_time = hdul[0].header["JD"]  # type: ignore
        bzero = hdul[0].header["BZERO"] if "BZERO" in hdul[0].header else 0  # type: ignore
        bscale = hdul[0].header["BSCALE"] if "BSCALE" in hdul[0].header else 1  # type: ignore
        image = FITSModel(filepath, data, obs_time, bzero, bscale)
        # Assuming image data is in the primary HDU
        return image


def load_images(image_paths: List[Path], image_manager: ImageManager):
    """Batch loads FITS images from list of paths"""
    images = [load_fits_image(f) for f in image_paths]
    for image in images:
        image_manager.add_image(image)


def remove_images(image_names: List[Path], image_manager: ImageManager):
    """Batch remove FITS images from application"""
    names = [f.name for f in image_names]
    images = []
    for name in names:
        image = image_manager.get_image(name)
        if image:
            images.append(image)
            image_manager.remove_image(image)
