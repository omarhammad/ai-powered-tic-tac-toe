import datetime
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class GameEvent:
    sessionId: str
    boardState: List[Optional[str]]
    currentPlayer: Optional[str]
    moveNumber: int
    gameStatus: str
    winner: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "sessionId": self.sessionId,
            "boardState": self.boardState,
            "currentPlayer": self.currentPlayer,
            "moveNumber": self.moveNumber,
            "gameStatus": self.gameStatus,
            "winner": self.winner,
            "occurredAt": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
