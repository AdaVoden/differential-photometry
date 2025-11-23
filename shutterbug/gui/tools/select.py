from .base_tool import Tool


class Select(Tool):

    def __init__(self):
        super().__init__()
        self._name = "Select"

    @property
    def name(self):
        return self._name

    def mouse_press(self, viewer, event):
        pass
