from typing import List, Literal

from pydantic import BaseModel, Field

from src.main.python.domain.TicTacToeState import TicTacToeState
from src.main.python.domain.enums.enums import Player, GameStatus


class TicTacToeStateModel(BaseModel):
    """
    JSON representation of TicTacToeState.
    """
    board: List[str] = Field(..., min_length=9, max_length=9)
    current_player: Literal["X", "O"]

    def to_domain(self):
        tmp = TicTacToeState(
            board=self.board,
            current_player=Player(self.current_player),
        )
        game_status = tmp._compute_status(tmp.board)

        return TicTacToeState(
            board=tmp.board,
            current_player=tmp.current_player,
            status=game_status
        )


class MoveResponse(BaseModel):
    index: int


class WinningProbaResponse(BaseModel):
    probability: float


class ErrorResponse(BaseModel):
    error: str
    status: str
