from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from shutterbug.gui.views.image import ImageViewer

import logging
from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtGui import QMouseEvent, QUndoCommand
from PySide6.QtWidgets import QWidget

from shutterbug.gui.operators.base_operator import BaseOperator
from shutterbug.gui.tools.base_tool import BaseTool


class ToolManager(QObject):
    tool_changed = Signal(BaseTool)
    operator_changed = Signal(BaseOperator)
    tool_settings_changed = Signal(QWidget)
    operator_finished = Signal()
    operator_cancelled = Signal()

    def __init__(self, viewer: ImageViewer):
        super().__init__()
        self._current_tool: BaseTool | None = None
        self.viewer = viewer
        self.active_operator: BaseOperator | None = None

    @property
    def tool(self):
        return self._current_tool

    @Slot(BaseTool)
    def set_tool(self, tool_cls):
        """Sets the current tool, as a class"""
        logging.debug(f"Setting current tool to: {tool_cls.__name__}")
        tool = tool_cls()
        self._current_tool = tool
        self.tool_changed.emit(tool)

    def begin_operation(self, event: QMouseEvent):
        """Creates operator and begins operation"""
        if not self._current_tool:
            return

        op = self._current_tool.create_operator(self.viewer)
        self.active_operator = op

        widget = op.create_settings_widget()
        self.tool_settings_changed.emit(widget)

        op.finished.connect(self._operator_finished)
        op.cancelled.connect(self._operator_cancelled)

        self.operator_changed.emit(op)
        op.start(event)

    def update_operation(self, event: QMouseEvent):
        """Updates current operation, if any"""
        if self.active_operator:
            self.active_operator.update(event)

    def end_operation_interaction(self):
        """Ends interaction phase of operator"""
        if self.active_operator:
            self.active_operator.stop_interaction()

    def end_operation_confirm(self):
        """Successfully ends current operation, if any"""
        if self.active_operator:
            self.active_operator.confirm()

    def end_operation_cancel(self):
        """Cancels current operation if any"""
        if self.active_operator:
            self.active_operator.cancel()

    @Slot(QUndoCommand)
    def _operator_finished(self, cmd: QUndoCommand | None):
        """Finished current operation by pushing command to stack"""
        self.active_operator = None
        if cmd is not None:
            print("Command is not none")
            self.viewer._undo_stack.push(cmd)
        self.operator_finished.emit()

    @Slot()
    def _operator_cancelled(self):
        """Cancels current operation"""
        self.active_operator = None
        self.operator_cancelled.emit()
