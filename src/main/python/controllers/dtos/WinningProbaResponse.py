from pydantic import BaseModel


class WinningProbaResponse(BaseModel):
    x: float
    o: float