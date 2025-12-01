STRETCH_REGISTRY = {}


def register_stretch(name: str):
    """Registers stretch to registry"""

    def decorator(cls):
        STRETCH_REGISTRY[name] = cls()
        return cls

    return decorator


def get_stretch(name: str):
    return STRETCH_REGISTRY.get(name)
