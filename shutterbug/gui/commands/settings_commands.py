from .base_command import BaseCommand
from shutterbug.core.models import GraphDataModel, FITSModel

import logging


class SetGraphValueCommand(BaseCommand):
    """Sets value in image"""

    def __init__(self, value_name: str, new_value, graph: GraphDataModel):
        super().__init__(f"Set Value: {value_name}")
        self.new_value = new_value
        self.graph = graph
        self.value_name = value_name
        self.old_value = graph.__getattribute__(value_name)

    def validate(self):
        pass

    def redo(self) -> None:
        logging.debug(f"COMMAND: Setting {self.value_name} to: {self.new_value}")
        self.graph.__setattr__(self.value_name, self.new_value)

    def undo(self) -> None:
        logging.debug(
            f"COMMAND: Undoing setting {self.value_name} to: {self.new_value}"
        )
        self.graph.__setattr__(self.value_name, self.new_value)


class SetImageValueCommand(BaseCommand):
    """Sets value in image"""

    def __init__(self, value_name: str, new_value, image: FITSModel):
        super().__init__(f"Set Value: {value_name}")
        self.new_value = new_value
        self.image = image
        self.value_name = value_name
        self.old_value = image.__getattribute__(value_name)

    def validate(self):
        pass

    def redo(self) -> None:
        logging.debug(f"COMMAND: Setting {self.value_name} to: {self.new_value}")
        self.image.__setattr__(self.value_name, self.new_value)

    def undo(self) -> None:
        logging.debug(
            f"COMMAND: Undoing setting {self.value_name} to: {self.new_value}"
        )
        self.image.__setattr__(self.value_name, self.new_value)
