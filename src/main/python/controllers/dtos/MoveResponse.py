from typing import Optional
from pydantic import BaseModel


class MoveResponse(BaseModel):
    board: list
    currentTurn: str
    isFinished: bool
    winner: Optional[str]
