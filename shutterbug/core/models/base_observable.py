#!/usr/bin/env python3

from PySide6.QtCore import QObject, Signal

from shutterbug.core.events import ChangeEvent


class ObservableQObject(QObject):
    """Dataclass-like observable QObject"""

    updated = Signal(ChangeEvent)

    def _define_field(self, name, default):
        """Creates setter and getter for field, emitting a changed signal on update"""
        private_name = f"_{name}"
        setattr(self, private_name, default)

        def getter(self):
            return getattr(self, private_name)

        def setter(self, value):
            if value != getattr(self, private_name):
                setattr(self, private_name, value)
                self.updated.emit(ChangeEvent(source=self, changed_fields={name}))

        setattr(self.__class__, name, property(getter, setter))
        return default
