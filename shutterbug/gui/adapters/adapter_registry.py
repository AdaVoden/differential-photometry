from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from shutterbug.core.app_controller import AppController
import logging
from typing import Any


class AdapterRegistry:

    def __init__(self, controller: AppController) -> None:
        super().__init__()

        self.controller = controller
        self._registry = {}

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
                return factory(obj, self.controller)
        return None
