from datetime import datetime
from typing import Optional, List

from domain.Board import Board
from domain.Mark import Mark
from domain.Rules import Rules
from services.LoggingService import LoggingService


class GameSession:
    def __init__(
            self,
            session_id: str,
            size: int = 3,
            player_x_id: str = "P1",
            player_o_id: str = "P2",
            logger: Optional[LoggingService] = None,
    ):
        self.session_id = session_id
        self.player_x_id = player_x_id
        self.player_o_id = player_o_id

        self.board = Board(size)
        self.rules = Rules(size)
        self.current_player = Mark.X
        self.winner: Optional[Mark] = None
        self.is_finished = False
        self.move_count = 0
        self.logger = logger  # injected dependency

        # Log initial state
        if self.logger:
            self.logger.log_state(
                session_id=self.session_id,
                board_state=self.board.get_state(),
                turn=self.current_player.value,
                move_count=self.move_count,
                timestamp=datetime.utcnow()
            )

    # ------------- Public API -------------

    def get_current_player(self) -> Mark:
        return self.current_player

    def get_board_state(self) -> List[Optional[str]]:
        return self.board.get_state()

    def make_move(self, slot_index: int) -> bool:
        if not self.board.valid_index(slot_index):
            return False

        if not self.board.is_slot_free(slot_index):
            return False

        # Apply move
        self.board.place_mark(slot_index, self.current_player)
        self.move_count += 1

        # Log the move
        if self.logger:
            self.logger.log_move(
                session_id=self.session_id,
                player_id=self._get_current_player_id(),
                board_state=self.board.get_state(),
                move_index=slot_index,
                timestamp=datetime.utcnow()
            )

        # Check game end conditions
        self._update_game_status()

        # Log new state (after move)
        if self.logger and not self.is_finished:
            self.logger.log_state(
                session_id=self.session_id,
                board_state=self.board.get_state(),
                turn=self.current_player.value,
                move_count=self.move_count,
                timestamp=datetime.utcnow()
            )

        # Switch turn if still running
        if not self.is_finished:
            self._switch_player()

        return True

    # ------------- Internal Helpers -------------

    def _update_game_status(self) -> None:
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
        self.current_player = Mark.O if self.current_player == Mark.X else Mark.X

    def _get_current_player_id(self) -> str:
        return self.player_x_id if self.current_player == Mark.X else self.player_o_id