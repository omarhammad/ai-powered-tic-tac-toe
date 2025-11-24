from dataclasses import dataclass
from typing import List, Optional

@dataclass
class GameEvent:
    sessionId: str
    boardState: List[Optional[str]]
    currentPlayer: Optional[str]            # "X", "O", or None when terminal
    moveNumber: int
    gameStatus: str                         # IN_PROGRESS / WIN_X / WIN_O / DRAW
    winner: Optional[str] = None            # "X", "O", or None

    def to_dict(self) -> dict:
        return {
            "sessionId": self.sessionId,
            "boardState": self.boardState,
            "currentPlayer": self.currentPlayer,
            "moveNumber": self.moveNumber,
            "gameStatus": self.gameStatus,
            "winner": self.winner,
        }
