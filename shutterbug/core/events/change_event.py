from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from shutterbug.core.models import FITSModel, StarMeasurement, ObservableQObject

from dataclasses import dataclass


@dataclass
class ChangeEvent:
    changed_fields: set


@dataclass
class UpdateEvent(ChangeEvent):
    source: ObservableQObject


@dataclass
class ImageUpdateEvent(ChangeEvent):
    source: FITSModel


@dataclass
class MeasurementUpdateEvent(ChangeEvent):
    source: StarMeasurement
