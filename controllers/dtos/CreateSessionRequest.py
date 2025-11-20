from typing import Optional
from pydantic import BaseModel


class CreateSessionRequest(BaseModel):
    playerX: Optional[str] = "P1"
    playerO: Optional[str] = "P2"
    playerXIsAI: bool = False
    playerOIsAI: bool = False
