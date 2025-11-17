from typing import Any


class AdapterRegistry:

    def __init__(self) -> None:
        self._registry = {}

    def register_adapter(self, cls: Any, adapter_factory):
        """Registers class to specific adapter factory"""
        self._registry[cls] = adapter_factory

    def get_adapter_for(self, obj: Any):
        """Retreives adapter factory for given object"""
        for cls, factory in self._registry.items():
            if isinstance(obj, cls):
                return factory(obj)
        return None
