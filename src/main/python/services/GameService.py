from datetime import datetime

from src.main.python.domain.GameSession import GameSession
from src.main.python.domain.Mark import Mark
from src.main.python.domain.Player import Player
from src.main.python.infrastructure.repositories.SessionRepository import SessionRepository


class GameService:
    """
    Application Service Layer:
    - Creates sessions
    - Handles moves (human or AI)
    - Enforces turn order
    - Performs ALL logging
    """

    def __init__(self, session_repository: SessionRepository, logging_service,
                 ai_strategy_x=None, ai_strategy_o=None):
        self.repo = session_repository
        self.logger = logging_service
        self.ai_x = ai_strategy_x
        self.ai_o = ai_strategy_o

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
            player_o_is_ai: bool = False
    ):

        player_x = Player(player_x_id, player_x_name, Mark.X, player_x_is_ai)
        player_o = Player(player_o_id, player_o_name, Mark.O, player_o_is_ai)
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
            if current.mark == current.mark.X and self.ai_x:
                move = self.ai_x.choose_move(session)
            elif current.mark == current.mark.O and self.ai_o:
                move = self.ai_o.choose_move(session)
            else:
                raise Exception("No AI strategy assigned for AI player")
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
            timestamp=datetime.utcnow()
        )

        # Log UPDATED state
        if not session.is_finished:
            self.logger.log_state(
                session_id=session.session_id,
                board_state=session.board.get_state(),
                turn=session.current_player.mark.value,
                move_count=session.move_count,
                timestamp=datetime.utcnow()
            )
        else:
            # Log final state
            result = (
                f"{session.winner.value}-wins"
                if session.winner else "draw"
            )
            self.logger.log_end(
                session_id=session.session_id,
                result=result,
                final_board_state=session.board.get_state(),
                timestamp=datetime.utcnow()
            )

        # Auto-play AI if needed
        if not session.is_finished and session.current_player.is_ai:
            return self.play_turn(session)

        return session
