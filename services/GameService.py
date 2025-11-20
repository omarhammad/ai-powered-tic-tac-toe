from domain.GameSession import GameSession
from infrastructure.repositories.SessionRepository import SessionRepository


class GameService:
    """
    Placeholder service layer reference.
    Replace this with your real GameService instance.
    """

    def __init__(self, session_repository: SessionRepository, logging_service, ai_strategy_x=None, ai_strategy_o=None):
        self.repo = session_repository
        self.logger = logging_service
        self.ai_x = ai_strategy_x
        self.ai_o = ai_strategy_o

    def create_session(self, session_id: str, player_x: str, player_o: str):

        session = GameSession(
            session_id=session_id,
            player_x_id=player_x,
            player_o_id=player_o,
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

        # AI or human handled inside GameService
        self.play_turn(session, human_move_index=move_index)

        return session

    # Uses the AI-aware logic from the previous layer
    def play_turn(self, session: GameSession, human_move_index=None):
        if session.is_finished:
            return session

        if session.current_player.value == "X" and self.ai_x:
            move = self.ai_x.choose_move(session)
        elif session.current_player.value == "O" and self.ai_o:
            move = self.ai_o.choose_move(session)
        else:
            move = human_move_index

        success = session.make_move(move)
        if not success:
            raise Exception("Invalid move")

        return session
