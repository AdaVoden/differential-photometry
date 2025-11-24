from abc import ABC, abstractmethod

from PySide6.QtWidgets import QWidget


class AbstractTool(ABC):

    @property
    @abstractmethod
    def name(self):
        raise NotImplementedError

    def mouse_press(self, viewer, event):
        pass

    def mouse_move(self, viewer, event):
        pass

    def mouse_release(self, viewer, event):
        pass

    def mouse_double_click(self, viewer, event):
        pass

    def key_press(self, viewer, event):
        pass

    def tool_panel(self) -> QWidget | None:
        raise NotImplementedError


class Tool(AbstractTool):

    def __init__(self) -> None:
        super().__init__()
        self._name = "BaseTool"

    @property
    def name(self):
        return self._name

    def tool_panel(self) -> QWidget | None:
        return None
