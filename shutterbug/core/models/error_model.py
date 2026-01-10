from dataclasses import dataclass

@dataclass
class ErrorModel:
    message: str
    severity: str
    retryable: bool
