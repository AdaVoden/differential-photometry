from pydantic import BaseModel

class Star(BaseModel):
    x: float
    y: float
    flux: float
    magnitude: float | None = None
    fwhm: float | None = None
    is_target: bool = False
    is_reference: bool = False