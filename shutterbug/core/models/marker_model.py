from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING
from uuid import uuid4

from PySide6.QtGui import QColor

if TYPE_CHECKING:
    from shutterbug.core.app_controller import AppController

from .base_observable import ObservableQObject


class MarkerType(Enum):
    DISPLAY = "display"
    APERTURE = "aperture"
    ANNULUS = "annulus"


class MarkerModel(ObservableQObject):

    type = "marker"

    def __init__(
        self,
        image_id: str,
        x: float,
        y: float,
        type: MarkerType,
        radius: float,
        colour: QColor,
        thickness: float,
        visible: bool,
        controller: AppController,
        parent=None,
    ):
        super().__init__(controller, parent)
        self.id = uuid4().hex
        self.image_id = image_id
        self.x = self._define_field("x", x)
        self.y = self._define_field("y", y)
        self.type = type
        self.radius = self._define_field("radius", radius)
        self.colour = self._define_field("colour", colour)
        self.thickness = self._define_field("thickness", thickness)
        self.visible = self._define_field("visible", visible)
