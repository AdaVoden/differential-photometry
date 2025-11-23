from PySide6.QtCore import QObject, Signal

from shutterbug.gui.tools.base_tool import Tool


class ToolManager(QObject):
    tool_changed = Signal(Tool)

    def __init__(self):
        super().__init__()
        self._current_tool: Tool | None = None

    @property
    def tool(self):
        return self._current_tool

    def set_tool(self, tool_cls):
        """Sets the current tool, as a class"""
        tool = tool_cls()
        self._current_tool = tool
        self.tool_changed.emit(tool)
