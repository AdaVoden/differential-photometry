from PySide6.QtCore import Signal, QObject

from shutterbug.gui.image_data import FITSImage

from typing import Dict, List

import logging


class ImageManager(QObject):
    """Manages multiple images and tracks which is active"""

    _instance = None

    images_added = Signal(list)
    active_image_changed = Signal(FITSImage)
    images_removed = Signal(list)

    def __init__(self):
        if not hasattr(self, "_initialized"):
            self._initialized = True

            super().__init__()
            self.images: Dict[str, FITSImage] = {}
            self.active_image: FITSImage | None = None

    def __new__(cls):
        if cls._instance is None:
            logging.debug("Creating Image Manager singleton")
            cls._instance = super().__new__(cls)

        return cls._instance

    def add_image(self, image: FITSImage):
        """Add image to manager"""
        self.images[image.filename] = image
        self.images_added.emit([image])
        if self.active_image is None:
            self.set_active_image(image)

    def add_images(self, images: List[FITSImage]):
        """Add multiple images to manager"""
        for image in images:
            self.images[image.filename] = image

        if images:  # if handed empty list
            self.images_added.emit(images)
            self.set_active_image(images[0])

    def set_active_image(self, image: FITSImage | None):
        """Sets active image"""
        if self.active_image != image:
            if image is None:
                logging.debug(f"Setting active image to None")
            else:
                logging.debug(f"Setting image as active: {image.filename}")
            self.active_image = image
            self.active_image_changed.emit(image)

    def remove_images(self, images: List[FITSImage]):
        """Removes image from manager"""
        for image in images:
            if image.filename in self.images.keys():
                self.images.pop(image.filename)

            if self.active_image == image:
                self.active_image = None
                self.active_image_changed.emit(self.active_image)
        self.images_removed.emit(images)

    def get_image(self, image_name: str) -> FITSImage | None:
        """Returns image from manager"""
        if image_name in self.images.keys():
            return self.images[image_name]
        return None
