from abc import abstractmethod, ABC

from typing import List

from PySide6.QtCore import QObject, Signal


class AdapterSignals(QObject):
    item_updated = Signal(object)
    item_removed = Signal(object)
    item_added = Signal(object)


class TabularDataInterface(ABC):
    @abstractmethod
    def get_column_headers(self) -> List[str]:
        raise NotImplementedError

    @abstractmethod
    def get_row_data(self) -> List:
        raise NotImplementedError

    @property
    @abstractmethod
    def signals(self) -> AdapterSignals:
        raise NotImplementedError
