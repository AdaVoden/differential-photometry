from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from shutterbug.core.models import FITSModel, ObservableQObject

from dataclasses import dataclass


@dataclass
class ChangeEvent:
    source: ObservableQObject
    changed_fields: set


@dataclass
class ImageUpdateEvent(ChangeEvent):
    source: FITSModel  # type: ignore
