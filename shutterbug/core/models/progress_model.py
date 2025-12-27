from dataclasses import dataclass
from uuid import uuid4


@dataclass
class ProgressModel:

    text: str
    current: int
    max: int
    uid: str = uuid4().hex
