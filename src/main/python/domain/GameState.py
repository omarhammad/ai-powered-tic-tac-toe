import datetime
from typing import List, Optional
from src.main.python.domain.enums.enums import Player, GameStatus, Difficulty


class GameState:
    """
    Represents one ML dataset row from AI self-play.
    """

    def __init__(
            self,
            game_session_id: str,
            move_number: int,
            board_state: List[Optional[str]],
            current_player: Player,
            legal_moves: List[int],
            action_taken: int,
            best_move_strong: int,
            outcome: GameStatus,
            reward: float,
            difficulty: Difficulty,
    ):
        self.game_session_id = game_session_id
        self.move_number = move_number
        self.board_state = board_state
        self.current_player = current_player
        self.legal_moves = legal_moves
        self.action_taken = action_taken
        self.best_move_strong = best_move_strong
        self.outcome = outcome
        self.reward = reward
        self.difficulty = difficulty

    def to_dict(self) -> dict:
        return {
            "gameSessionId": self.game_session_id,
            "moveNumber": self.move_number,
            "boardState": self.board_state,
            "currentPlayer": self.current_player.value,
            "legalMoves": self.legal_moves,
            "actionTaken": self.action_taken,
            "bestMoveStrong": self.best_move_strong,
            "outcome": self.outcome.value,
            "reward": self.reward,
            "difficulty": self.difficulty.value,
            "occurredAt": datetime.datetime.utcnow().replace(microsecond=0).isoformat()

        }
