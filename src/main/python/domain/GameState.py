from dataclasses import dataclass
from typing import List, Optional

@dataclass
class GameState:
    sessionId: str
    boardState: List[Optional[str]]          # ["X", None, ...]
    currentPlayer: str                       # "X" or "O"
    legalMoves: List[int]                    # [1, 2, 5, ...]
    actionTaken: Optional[int] = None        # move index chosen
    moveNumber: int = 0                      # 1..9
    gameStatus: str = "IN_PROGRESS"          # IN_PROGRESS / WIN_X / WIN_O / DRAW
    reward: Optional[int] = None             # +1 / 0 / -1 (only on terminal)

    def to_dict(self):
        """Convert GameState to serializable dict for logging."""
        return {
            "sessionId": self.sessionId,
            "boardState": self.boardState,
            "currentPlayer": self.currentPlayer,
            "legalMoves": self.legalMoves,
            "actionTaken": self.actionTaken,
            "moveNumber": self.moveNumber,
            "gameStatus": self.gameStatus,
            "reward": self.reward
        }
