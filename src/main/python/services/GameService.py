from typing import Optional

from src.main.python.domain.GameSession import GameSession
from src.main.python.domain.Mark import Mark
from src.main.python.domain.Player import Player
from src.main.python.events.GameEvent import GameEvent
from src.main.python.infrastructure.messaging.GameBcPublisher import GameBcPublisher
from src.main.python.infrastructure.repositories.SessionRepository import SessionRepository
from src.main.python.infrastructure.clients.ai_client.ExternalAIClient import ExternalAIClient


class GameService:
    """
    Application Service Layer:
    - Handles human moves
    - Handles AI moves through moveIndex = -1
    - Auto-chains AI turns
    - Publishes GameEvent to GameBC (platform)
    - AI vs AI sessions are not allowed
    """

    def __init__(
            self,
            session_repository: SessionRepository,
            game_bc_publisher: GameBcPublisher,
            ai_client: ExternalAIClient,
            default_ai_difficulty: str = "medium",
    ):
        self.repo = session_repository
        self.game_bc_publisher = game_bc_publisher
        self.ai_client = ai_client
        self.default_ai_difficulty = default_ai_difficulty

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
            player_x_is_ai: bool,
            player_o_is_ai: bool,
            player_x_ai_difficulty: Optional[str] = None,
            player_o_ai_difficulty: Optional[str] = None,
    ):

        # BLOCK AI vs AI sessions
        if player_x_is_ai and player_o_is_ai:
            raise Exception("AI vs AI sessions are not allowed. Use AI subsystem for self-play.")

        player_x = Player(
            player_id=player_x_id,
            player_name=player_x_name,
            mark=Mark.X,
            is_ai=player_x_is_ai,
            difficulty=player_x_ai_difficulty
        )

        player_o = Player(
            player_id=player_o_id,
            player_name=player_o_name,
            mark=Mark.O,
            is_ai=player_o_is_ai,
            difficulty=player_o_ai_difficulty
        )

        session = GameSession(session_id, player_x, player_o)
        self.repo.save(session_id, session)
        return session

    # -------------------------------------------------------
    # SESSION GET
    # -------------------------------------------------------
    def get_session(self, session_id: str):
        return self.repo.find(session_id)

    # -------------------------------------------------------
    # MOVE HANDLING (HUMAN + AI)
    # -------------------------------------------------------
    def apply_move(self, session_id: str, player_id: str, move_index: int):
        session: GameSession = self.repo.find(session_id)
        if not session:
            raise ValueError("Session not found")

        if session.is_finished:
            return session

        current = session.current_player

        # HUMAN TURN
        if not current.is_ai:
            if player_id != current.player_id:
                raise Exception("It's not your turn")

            if move_index < 0 or move_index > 8:
                raise Exception("Invalid human moveIndex")

            return self._play_turns(session, human_move_index=move_index)

        # AI TURN
        if current.is_ai:
            if move_index != -1:
                raise Exception("AI moveIndex must be -1")

            return self._play_turns(session, human_move_index=None)

    # -------------------------------------------------------
    # TURN SEQUENCING
    # -------------------------------------------------------
    def _play_turns(self, session: GameSession, human_move_index=None):

        if session.is_finished:
            return session

        mover = session.current_player
        if mover.is_ai:
            move = self._choose_ai_move(session, mover)
        else:
            move = human_move_index

        if move is None:
            raise Exception("Human move required")

        if not session.make_move(move):
            raise Exception("Invalid move")

        self._publish_game_event(session, mover)

        return session

    # -------------------------------------------------------
    # AI SELECTION
    # -------------------------------------------------------
    def _choose_ai_move(self, session: GameSession, player: Player) -> int:
        difficulty = player.difficulty or self.default_ai_difficulty
        return self.ai_client.choose_move(session, difficulty=difficulty)

    # -------------------------------------------------------
    # PLATFORM LOGGING ONLY
    # -------------------------------------------------------
    def _publish_game_event(self, session: GameSession, mover: Player):

        if session.is_finished:
            if session.winner is None:
                game_status = "DRAW"
                winner_id = None
            else:
                winner_mark = session.winner.value
                winner_player = (
                    session.player_x if session.player_x.mark.value == winner_mark
                    else session.player_o
                )
                winner_id = winner_player.player_id
                game_status = f"{winner_mark}_WON"
        else:
            game_status = "IN_PROGRESS"
            winner_id = None

        game_event = GameEvent(
            sessionId=session.session_id,
            boardState=session.board.get_state(),
            currentPlayer=None if session.is_finished else session.current_player.player_id,
            moveNumber=session.move_count,
            gameStatus=game_status,
            winner=winner_id,
        )

        self.game_bc_publisher.publish_state(game_event)
