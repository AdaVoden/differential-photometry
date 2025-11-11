#!/usr/bin/env python3

from PySide6.QtCore import QObject, Signal


class ObservableQObject(QObject):
    """Dataclass-like observable QObject"""

    updated = Signal(object)

    def _define_field(self, name, default):
        private_name = f"_{name}"
        setattr(self, private_name, default)

        def getter(self):
            return getattr(self, private_name)

        def setter(self, value):
            if value != getattr(self, private_name):
                setattr(self, private_name, value)
                self.updated.emit(self)

        setattr(self.__class__, name, property(getter, setter))
