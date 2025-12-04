from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, List

from shutterbug.core.events.change_event import Event, EventDomain
from shutterbug.core.managers.base_manager import BaseManager
from shutterbug.core.models import FITSModel

if TYPE_CHECKING:
    from shutterbug.core.app_controller import AppController

from astropy.io import fits

import logging


class FileManager(BaseManager):

    filetypes = {".fits", ".fit", ".fts"}

    def __init__(self, controller: AppController, parent=None):
        super().__init__(controller, parent)

    def load(self, path: Path):
        """Loads target path into system"""
        if {path.suffix} & self.filetypes:
            image = self._load_fits_image(path)
            self.controller.dispatch(Event(EventDomain.FILE, "load", data=image))
            return image

    def _load_fits_image(self, path: Path):
        logging.debug(f"Loading FITS image from {path}")

        with fits.open(
            path, uint=True, memmap=True, do_not_scale_image_data=True
        ) as hdul:
            data = hdul[0].data  # type: ignore
            obs_time = hdul[0].header["JD"]  # type: ignore
            bzero = hdul[0].header["BZERO"] if "BZERO" in hdul[0].header else 0  # type: ignore
            bscale = hdul[0].header["BSCALE"] if "BSCALE" in hdul[0].header else 1  # type: ignore
            image = FITSModel(self.controller, path, data, obs_time, bzero, bscale)
            # Assuming image data is in the primary HDU
            return image
