from typing import Any, Optional


from enum import Enum
from dataclasses import dataclass


class EventDomain(Enum):
    IMAGE = "image"
    MEASUREMENT = "measurement"
    GRAPH = "graph"
    STAR = "star"
    TOOL = "tool"
    OPERATOR = "operator"
    ADAPTER = "adapter"
    FILE = "file"


@dataclass
class Event:
    domain: EventDomain
    action: str
    field: Optional[str] = None
    data: Optional[Any] = None

    @property
    def key(self):
        if self.field:
            return f"{self.domain.value}.{self.action}.{self.field}"
        return f"{self.domain.value}.{self.action}"
