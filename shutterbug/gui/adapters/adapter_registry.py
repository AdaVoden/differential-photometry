import logging
from typing import Any


class AdapterRegistry:

    _instance = None

    def __init__(self) -> None:
        if not hasattr(self, "_initialized"):
            self._initialized = True
            super().__init__()

            self._registry = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    def register_adapter(self, cls: Any, adapter_factory):
        """Registers class to specific adapter factory"""
        logging.debug(
            f"Registering class {cls.__name__} to adapter {adapter_factory.__name__}"
        )
        self._registry[cls] = adapter_factory

    def get_adapter_for(self, obj: Any):
        """Retreives adapter factory for given object"""
        for cls, factory in self._registry.items():
            if isinstance(obj, cls):
                return factory(obj)
        return None
