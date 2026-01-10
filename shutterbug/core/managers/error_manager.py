from PySide6.QtCore import Signal

from shutterbug.core.models import ErrorModel
from .base_manager import BaseManager


class ErrorManager(BaseManager):
    error_raised = Signal(ErrorModel)

    def raise_error(self, message: str, severity: str, retryable: bool = False):
        """raises error with the system"""
        self.error_raised.emit(ErrorModel(message, severity, retryable))
