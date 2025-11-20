from datetime import datetime
from typing import Optional, List

from domain.Board import Board
from domain.Mark import Mark
from domain.Player import Player
from domain.Rules import Rules
from services.LoggingService import LoggingService


class GameSession:
    """
    Domain object representing a single Tic-Tac-Toe match.
    """

    def __init__(
            self,
            session_id: str,
            player_x_id: str,
            player_o_id: str,
            size: int = 3,
            player_x_is_ai: bool = False,
            player_o_is_ai: bool = False,
            logger: Optional[LoggingService] = None,
    ):
        self.session_id = session_id

        # Players (must supply IDs)
        self.player_x = Player(player_x_id, Mark.X, is_ai=player_x_is_ai)
        self.player_o = Player(player_o_id, Mark.O, is_ai=player_o_is_ai)

        # Game state
        self.board = Board(size)
        self.rules = Rules(size)
        self.current_player: Player = self.player_x
        self.winner: Optional[Mark] = None
        self.is_finished = False
        self.move_count = 0

        # Logging
        self.logger = logger

        if self.logger:
            self.logger.log_state(
                session_id=self.session_id,
                board_state=self.board.get_state(),
                turn=self.current_player.mark.value,
                move_count=self.move_count,
                timestamp=datetime.utcnow()
            )

    # -------------------------
    # PUBLIC API
    # -------------------------

    def get_current_player(self) -> Player:
        return self.current_player

    def get_board_state(self) -> List[Optional[str]]:
        return self.board.get_state()

    def make_move(self, slot_index: int) -> bool:
        """
        Attempts to place a mark for the current player.
        Returns True if successful, False if illegal move.
        """

        # Validate index
        if not self.board.valid_index(slot_index):
            return False

        # Cell must be free
        if not self.board.is_slot_free(slot_index):
            return False

        # Apply move
        self.board.place_mark(slot_index, self.current_player.mark)
        self.move_count += 1

        # Log move
        if self.logger:
            self.logger.log_move(
                session_id=self.session_id,
                player_id=self.current_player.player_id,
                board_state=self.board.get_state(),
                move_index=slot_index,
                timestamp=datetime.utcnow()
            )

        # Update state (win/draw)
        self._update_game_status()

        # Log updated board (if game continues)
        if self.logger and not self.is_finished:
            self.logger.log_state(
                session_id=self.session_id,
                board_state=self.board.get_state(),
                turn=self.current_player.mark.value,
                move_count=self.move_count,
                timestamp=datetime.utcnow()
            )

        # Switch turns only if game isn't over
        if not self.is_finished:
            self._switch_player()

        return True

    # -------------------------
    # INTERNAL HELPERS
    # -------------------------

    def _update_game_status(self) -> None:
        """
        Checks for win/draw conditions and logs final state.
        """
        winner = self.rules.check_winner(self.board)

        if winner:
            self.winner = winner
            self.is_finished = True

            if self.logger:
                self.logger.log_end(
                    session_id=self.session_id,
                    result=f"{winner.value}-wins",
                    final_board_state=self.board.get_state(),
                    timestamp=datetime.utcnow()
                )
            return

        # Draw
        if self.rules.is_draw(self.board):
            self.is_finished = True

            if self.logger:
                self.logger.log_end(
                    session_id=self.session_id,
                    result="draw",
                    final_board_state=self.board.get_state(),
                    timestamp=datetime.utcnow()
                )

    def _switch_player(self) -> None:
        """
        Switch turns between X and O.
        """
        self.current_player = (
            self.player_o if self.current_player == self.player_x else self.player_x
        )