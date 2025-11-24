from datetime import datetime
from typing import Dict, Optional

from src.main.python.domain.GameSession import GameSession
from src.main.python.domain.Mark import Mark
from src.main.python.domain.Player import Player
from src.main.python.infrastructure.repositories.SessionRepository import SessionRepository
from src.main.python.services.AiStrategy import AiStrategy


class GameService:
    """
    Application Service Layer:
    - Creates sessions
    - Handles moves (human or AI)
    - Enforces turn order
    - Performs ALL logging
    """

    def __init__(
        self,
        session_repository: SessionRepository,
        logging_service,
        ai_strategies: Dict[str, AiStrategy],
        default_ai_type: str = "mcts_medium",
    ):
        self.repo = session_repository
        self.logger = logging_service
        self.ai_strategies = ai_strategies
        self.default_ai_type = default_ai_type

        if self.default_ai_type not in self.ai_strategies:
            raise ValueError(
                f"Default AI type '{self.default_ai_type}' is not in ai_strategies"
            )

    # -------------------------------------------------------
    # SESSION CREATION
    # -------------------------------------------------------
    def create_session(
        self,
        session_id: str,
        player_x_id: str,
        player_o_id: str,
        player_x_name: str,
        player_o_name: str,
        player_x_is_ai: bool = False,
        player_o_is_ai: bool = False,
        player_x_ai_type: Optional[str] = None,
        player_o_ai_type: Optional[str] = None,
    ):
        player_x = Player(
            player_x_id,
            player_x_name,
            Mark.X,
            player_x_is_ai,
            self._resolve_ai_type(player_x_is_ai, player_x_ai_type),
        )
        player_o = Player(
            player_o_id,
            player_o_name,
            Mark.O,
            player_o_is_ai,
            self._resolve_ai_type(player_o_is_ai, player_o_ai_type),
        )
        session = GameSession(
            session_id,
            player_x,
            player_o,
        )

        # Log initial state
        self.logger.log_state(
            session_id=session.session_id,
            board_state=session.board.get_state(),
            turn=session.current_player.mark.value,
            move_count=session.move_count,
            timestamp=datetime.utcnow()
        )

        self.repo.save(session_id, session)
        return session

    # -------------------------------------------------------
    def get_session(self, session_id: str):
        return self.repo.find(session_id)

    # -------------------------------------------------------
    # APPLY HUMAN MOVE
    # -------------------------------------------------------
    def apply_move(self, session_id: str, player_id: str, move_index: int):
        session: GameSession = self.repo.find(session_id)
        if not session:
            raise ValueError("Session not found")

        current = session.current_player

        if current.is_ai:
            raise Exception("It is the AI's turn, human move not allowed")

        if player_id != current.player_id:
            raise Exception("It's not your turn")

        return self.play_turn(session, human_move_index=move_index)

    # -------------------------------------------------------
    # PLAY TURN (AI or Human)
    # -------------------------------------------------------
    def play_turn(self, session: GameSession, human_move_index=None):
        if session.is_finished:
            return session

        current = session.current_player

        # Decide move source
        if current.is_ai:
            move = self._choose_ai_move(session, current)
        else:
            move = human_move_index

        success = session.make_move(move)
        if not success:
            raise Exception("Invalid move")

        # Log AFTER applying the move
        self.logger.log_move(
            session_id=session.session_id,
            player_id=current.player_id,
            board_state=session.board.get_state(),
            move_index=move,
            timestamp=datetime.utcnow(),
        )

        # Log UPDATED state
        if not session.is_finished:
            self.logger.log_state(
                session_id=session.session_id,
                board_state=session.board.get_state(),
                turn=session.current_player.mark.value,
                move_count=session.move_count,
                timestamp=datetime.utcnow(),
            )
        else:
            # Log final state
            result = f"{session.winner.value}-wins" if session.winner else "draw"
            self.logger.log_end(
                session_id=session.session_id,
                result=result,
                final_board_state=session.board.get_state(),
                timestamp=datetime.utcnow(),
            )

        # Auto-play AI if needed
        if not session.is_finished and session.current_player.is_ai:
            return self.play_turn(session)

        return session

    # -------------------------------------------------------
    # AI helpers
    # -------------------------------------------------------
    def _resolve_ai_type(self, is_ai: bool, requested_type: Optional[str]) -> Optional[str]:
        if not is_ai:
            return None
        if requested_type:
            return requested_type
        # AI and no explicit type → use default (we know it exists in ai_strategies)
        return self.default_ai_type

    def _choose_ai_move(self, session: GameSession, player: Player) -> int:
        ai_type = player.ai_type
        if not ai_type:
            # Should not happen if _resolve_ai_type is always used for AI players
            raise Exception("AI player has no ai_type set")

        strategy = self.ai_strategies.get(ai_type)
        if not strategy:
            raise Exception(f"Unknown AI type '{ai_type}'")

        return strategy.choose_move(session)
