from domain.GameSession import GameSession, Player
from infrastructure.clients.LoggingClient import LoggingClient
from infrastructure.repositories.SessionRepository import SessionRepository


class GameService:
    """
    Service Layer:
    - Creates sessions
    - Handles moves
    - Enforces turn order
    - Handles AI or human turns
    """

    def __init__(self, session_repository: SessionRepository, logging_service,
                 ai_strategy_x=None, ai_strategy_o=None):
        self.repo = session_repository
        self.logger = logging_service
        self.ai_x = ai_strategy_x
        self.ai_o = ai_strategy_o

    def create_session(
            self,
            session_id: str,
            player_x: str,
            player_o: str,
            player_x_is_ai: bool = False,
            player_o_is_ai: bool = False
    ):
        session = GameSession(
            session_id=session_id,
            player_x_id=player_x,
            player_o_id=player_o,
            player_x_is_ai=player_x_is_ai,
            player_o_is_ai=player_o_is_ai,
            logger=self.logger
        )
        self.repo.save(session_id, session)
        return session

    def get_session(self, session_id: str):
        return self.repo.find(session_id)

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

    def play_turn(self, session: GameSession, human_move_index=None):
        if session.is_finished:
            return session

        current = session.current_player

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

        if not session.is_finished and session.current_player.is_ai:
            return self.play_turn(session)

        return session
