STRETCH_REGISTRY = {}


def register_stretch(name):
    """Registers stretch to registry"""

    def decorator(cls):
        STRETCH_REGISTRY[name] = cls()
        return cls

    return decorator
