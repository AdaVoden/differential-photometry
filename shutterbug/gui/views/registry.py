from typing import Type
from shutterbug.gui.views.base_view import BaseView


VIEW_REGISTRY = {}


def register_view():
    """Registers view to registry"""

    def decorator(cls: Type[BaseView]):
        VIEW_REGISTRY[cls.name] = cls

        return cls

    return decorator
