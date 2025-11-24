from __future__ import annotations

from dataclasses import dataclass
from typing import List

from src.main.python.domain.Board import Board
from src.main.python.domain.Mark import Mark
from src.main.python.domain.Rules import Rules
from src.main.python.services.mcts.GameState import GameState


@dataclass(frozen=True)
class TicTacToeState(GameState):
    """Immutable Tic-Tac-Toe snapshot used during tree search."""

    cells: List[Mark]
    current_mark: Mark
    rules: Rules

    @classmethod
    def from_session(cls, session) -> "TicTacToeState":
        board_copy = list(session.board.cells)
        return cls(board_copy, session.current_player.mark, session.rules)

    def current_player(self) -> Mark:
        return self.current_mark

    def legal_moves(self) -> List[int]:
        return [idx for idx, cell in enumerate(self.cells) if cell == Mark.EMPTY]

    def next_state(self, move: int) -> "TicTacToeState":
        new_cells = list(self.cells)
        new_cells[move] = self.current_mark
        next_mark = Mark.O if self.current_mark == Mark.X else Mark.X
        return TicTacToeState(new_cells, next_mark, self.rules)

    def is_terminal(self) -> bool:
        board = self._to_board(self.cells)
        return self.rules.check_winner(board) is not None or self.rules.is_draw(board)

    def result(self, perspective_player: Mark) -> float:
        board = self._to_board(self.cells)
        winner = self.rules.check_winner(board)
        if winner is None:
            if self.rules.is_draw(board):
                return 0.5
            raise ValueError("Result called on non-terminal state")
        return 1.0 if winner == perspective_player else 0.0

    def _to_board(self, cells: List[Mark]) -> Board:
        board = Board(self.rules.size)
        board.cells = list(cells)
        return board
