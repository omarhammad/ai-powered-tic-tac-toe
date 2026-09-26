from dataclasses import field, dataclass
from typing import List, Optional

from src.main.python.domain.enums.enums import Player, GameStatus


@dataclass
class TicTacToeState:
    """
    Pure domain representation of a Tic-Tac-Toe board state.

    - board: list of 9 strings: "X", "O", or " "
    - current_player: whose turn it is
    - status: game status (RUNNING, X_WINS, O_WINS, DRAW)
    """

    board: List[str] = field(default_factory=lambda: [" "] * 9)
    current_player: Player = Player.X
    status: GameStatus = GameStatus.IN_PROGRESS

    def legal_moves(self) -> List[int]:
        """Return indices of empty cells (legal moves)."""
        if self.status != GameStatus.IN_PROGRESS:
            return []
        return [i for i, v in enumerate(self.board) if v == " "]

    def is_terminal(self) -> bool:
        """True if game is over (win or draw)."""
        return self.status != GameStatus.IN_PROGRESS

    def winner(self) -> Optional[Player]:
        """Return the winning player, or None if no winner."""
        if self.status == GameStatus.X_WON:
            return Player.X
        if self.status == GameStatus.O_WON:
            return Player.O
        return None

    def apply_move(self, move_index: int) -> "TicTacToeState":
        """
        Return a NEW TicTacToeState with the move applied.
        Does not mutate the original state.
        """
        if move_index not in range(9):
            raise ValueError("Move index must be between 0 and 8.")
        if move_index not in self.legal_moves():
            raise ValueError("Illegal move: cell not empty or game already finished.")

        new_board = list(self.board)
        new_board[move_index] = self.current_player.value

        # Next player
        next_player = Player.O if self.current_player == Player.X else Player.X

        # Compute new game status
        new_status = self._compute_status(new_board)

        return TicTacToeState(
            board=new_board,
            current_player=next_player,
            status=new_status,
        )

    # -------------------- internal helpers --------------------

    @staticmethod
    def _compute_status(board: List[str]) -> GameStatus:
        lines = [
            (0, 1, 2),
            (3, 4, 5),
            (6, 7, 8),
            (0, 3, 6),
            (1, 4, 7),
            (2, 5, 8),
            (0, 4, 8),
            (2, 4, 6),
        ]

        for a, b, c in lines:
            if board[a] != " " and board[a] == board[b] == board[c]:
                return GameStatus.X_WON if board[a] == "X" else GameStatus.O_WON

        if " " not in board:
            return GameStatus.DRAW

        return GameStatus.IN_PROGRESS