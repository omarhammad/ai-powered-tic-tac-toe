from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Any


class GameState(ABC):
    """Abstract game state contract consumed by MCTS."""

    @abstractmethod
    def current_player(self) -> Any:
        """Return the player/mark that will act from this state."""

    @abstractmethod
    def legal_moves(self) -> List[int]:
        """Return all legal moves from this state."""

    @abstractmethod
    def next_state(self, move: int) -> "GameState":
        """Return the state reached after applying the given move."""

    @abstractmethod
    def is_terminal(self) -> bool:
        """Return True when the game is over for this state."""

    @abstractmethod
    def result(self, perspective_player: Any) -> float:
        """Return 1.0 (win), 0.5 (draw), or 0.0 (loss) for the perspective player."""
