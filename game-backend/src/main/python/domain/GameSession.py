from typing import Optional, List

from src.main.python.domain.Board import Board
from src.main.python.domain.Mark import Mark
from src.main.python.domain.Player import Player
from src.main.python.domain.Rules import Rules


class GameSession:
    """
    Pure domain object representing a single Tic-Tac-Toe match.
    Contains NO logging, NO external service calls.
    """

    def __init__(
            self,
            session_id: str,
            player_x : Player,
            player_o : Player,
            size: int = 3,

    ):
        self.session_id = session_id
        self.player_x = player_x
        self.player_o = player_o
        # Game state
        self.board = Board(size)
        self.rules = Rules(size)
        self.current_player: Player = self.player_x
        self.winner: Optional[Mark] = None
        self.is_finished = False
        self.move_count = 0

    # -------------------------
    # PUBLIC DOMAIN OPERATIONS
    # -------------------------

    def get_current_player(self) -> Player:
        return self.current_player

    def get_board_state(self) -> List[Optional[str]]:
        return self.board.get_state()

    def make_move(self, slot_index: int) -> bool:
        """
        Pure domain action:
        - validates move
        - applies mark
        - checks game status
        - switches turn
        """

        if not self.board.valid_index(slot_index):
            return False

        if not self.board.is_slot_free(slot_index):
            return False

        # Apply move
        self.board.place_mark(slot_index, self.current_player.mark)
        self.move_count += 1

        # Update game end conditions
        self._update_game_status()

        # Switch turns if still playing
        if not self.is_finished:
            self._switch_player()

        return True

    # -------------------------
    # INTERNAL HELPERS
    # -------------------------

    def _update_game_status(self) -> None:
        winner = self.rules.check_winner(self.board)

        if winner:
            self.winner = winner
            self.is_finished = True
            return

        if self.rules.is_draw(self.board):
            self.is_finished = True

    def _switch_player(self) -> None:
        """
        Switch turns between X and O.
        """
        self.current_player = (
            self.player_o if self.current_player == self.player_x else self.player_x
        )
