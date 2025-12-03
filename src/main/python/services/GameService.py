from typing import Dict

from src.main.python.domain.GameSession import GameSession
from src.main.python.domain.Mark import Mark
from src.main.python.domain.Player import Player
from src.main.python.events.GameEvent import GameEvent
from src.main.python.infrastructure.clients.logging_client.MlLoggingClient import MlLoggingClient
from src.main.python.infrastructure.messaging.GameBcPublisher import GameBcPublisher
from src.main.python.infrastructure.repositories.SessionRepository import SessionRepository
from src.main.python.domain.GameState import GameState
from src.main.python.infrastructure.clients.ai_client.ExternalAIClient import ExternalAIClient


class GameService:
    """
    Application Service Layer:
    - Handles human moves
    - Handles AI moves through moveIndex = -1
    - Auto-chains AI turns
    - Logs game states to ML service
    - Publishes events only when a human is involved
    """

    def __init__(
            self,
            session_repository: SessionRepository,
            ml_logger: MlLoggingClient,
            game_bc_publisher: GameBcPublisher,
            ai_client: ExternalAIClient,
            default_ai_difficulty: str = "medium",
    ):
        self.repo = session_repository
        self.ml_logger = ml_logger
        self.game_bc_publisher = game_bc_publisher
        self.ai_client = ai_client
        self.default_ai_difficulty = default_ai_difficulty

        # Store difficulty per AI player
        self.player_difficulties: Dict[str, str] = {}

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
    ):

        player_x = Player(player_x_id, player_x_name, Mark.X, player_x_is_ai)
        player_o = Player(player_o_id, player_o_name, Mark.O, player_o_is_ai)

        session = GameSession(session_id, player_x, player_o)

        # init AI difficulties
        if player_x_is_ai:
            self.player_difficulties[player_x_id] = self.default_ai_difficulty
        if player_o_is_ai:
            self.player_difficulties[player_o_id] = self.default_ai_difficulty

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
        """
        Supports:
        - Human moves (moveIndex = 0–8)
        - AI moves    (moveIndex = -1)
        """
        session: GameSession = self.repo.find(session_id)
        if not session:
            raise ValueError("Session not found")

        if session.is_finished:
            return session

        current = session.current_player

        # -------------------------------------------------
        # HUMAN TURN
        # -------------------------------------------------
        if not current.is_ai:
            if player_id != current.player_id:
                raise Exception("It's not your turn")

            if move_index < 0 or move_index > 8:
                raise Exception("Invalid human moveIndex")

            return self._play_turns(session, human_move_index=move_index)

        # -------------------------------------------------
        # AI TURN (moveIndex MUST be -1)
        # -------------------------------------------------
        if current.is_ai:
            if move_index != -1:
                raise Exception("AI moveIndex must be -1")

            return self._play_turns(session, human_move_index=None)

    # -------------------------------------------------------
    # TURN SEQUENCING
    # -------------------------------------------------------
    def _play_turns(self, session: GameSession, human_move_index=None):
        """
        Executes the human move OR the first AI move,
        then continues triggering AI moves until:
        - game ends, or
        - it's a human's turn again
        """

        if session.is_finished:
            return session

        # First move this turn
        mover = session.current_player
        if mover.is_ai:
            move = self._choose_ai_move(session, mover)
        else:
            move = human_move_index

        if move is None:
            raise Exception("Human move required")

        if not session.make_move(move):
            raise Exception("Invalid move")

        self._log_after_move(session, mover, move)

        # Chain additional AI moves
        while not session.is_finished and session.current_player.is_ai:
            mover = session.current_player
            ai_move = self._choose_ai_move(session, mover)

            if not session.make_move(ai_move):
                raise Exception(f"AI selected illegal move: {ai_move}")

            self._log_after_move(session, mover, ai_move)

        return session

    # -------------------------------------------------------
    # AI SELECTION
    # -------------------------------------------------------
    def _get_difficulty(self, player: Player) -> str:
        return self.player_difficulties.get(player.player_id, self.default_ai_difficulty)

    def _choose_ai_move(self, session: GameSession, player: Player) -> int:
        difficulty = self._get_difficulty(player)
        return self.ai_client.choose_move(session, difficulty=difficulty)

    # -------------------------------------------------------
    # LOGGING
    # -------------------------------------------------------
    def _log_after_move(self, session: GameSession, mover: Player, move_index: int):
        """
        Logs ML state for every move
        Publishes GameEvent only when humans are present
        """

        if session.is_finished:
            if session.winner is None:
                game_status = "DRAW"
                reward = 0
                winner_id = None
            else:
                winner_mark = session.winner.value
                winner_player = (
                    session.player_x if session.player_x.mark.value == winner_mark
                    else session.player_o
                )
                winner_id = winner_player.player_id
                game_status = f"{winner_mark}_WON"
                reward = 1 if mover.mark.value == winner_mark else -1
        else:
            game_status = "IN_PROGRESS"
            reward = None
            winner_id = None

        # Always log to ML service
        ml_state = GameState(
            sessionId=session.session_id,
            boardState=session.board.get_state(),
            currentPlayer=mover.mark.value,
            legalMoves=session.board.get_legal_moves(),
            actionTaken=move_index,
            moveNumber=session.move_count,
            gameStatus=game_status,
            reward=reward,
        )
        self.ml_logger.log_game_state(ml_state)

        # Skip GameBC when AI vs AI
        if session.player_x.is_ai and session.player_o.is_ai:
            return

        # Publish GameEvent
        game_event = GameEvent(
            sessionId=session.session_id,
            boardState=session.board.get_state(),
            currentPlayer=None if session.is_finished else session.current_player.player_id,
            moveNumber=session.move_count,
            gameStatus=game_status,
            winner=winner_id,
        )
        self.game_bc_publisher.publish_state(game_event)
