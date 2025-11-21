from pydantic import BaseModel


class MoveRequest(BaseModel):
    sessionId: str
    playerId: str
    moveIndex: int