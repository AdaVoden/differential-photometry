from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from shutterbug.core.app_controller import AppController

from PySide6.QtCore import QObject, Signal

from shutterbug.core.events import Event, EventDomain


class ObservableQObject(QObject):
    """Dataclass-like observable QObject"""

    updated = Signal(Event)
    type = "base"

    def __init__(self, controller: AppController, parent=None):
        super().__init__(parent)
        self.controller = controller

    def _define_field(self, name, default):
        """Creates setter and getter for field, emitting a changed signal on update"""
        private_name = f"_{name}"
        setattr(self, private_name, default)

        def getter(self):
            return getattr(self, private_name)

        def setter(self, value):
            if value != getattr(self, private_name):
                setattr(self, private_name, value)
                self.controller.dispatch(
                    Event(EventDomain[self.type], "updated", name, data=value)
                )

        setattr(self.__class__, name, property(getter, setter))
        return default
