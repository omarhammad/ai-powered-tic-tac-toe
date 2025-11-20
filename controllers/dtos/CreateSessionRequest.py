from typing import Optional

from pydantic import BaseModel


class CreateSessionRequest(BaseModel):
    playerX: Optional[str] = "P1"
    playerO: Optional[str] = "P2"

