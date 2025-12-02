from abc import ABC, abstractmethod

from src.main.python.domain.TicTacToeState import TicTacToeState


class AIModel(ABC):
    """Generic AI Strategy Interface (MCTS, ML, hybrid...)."""

    @abstractmethod
    def choose_move(self, state: TicTacToeState, simulations: int) -> int:
        pass

    @abstractmethod
    def winning_probability(self, state: TicTacToeState, simulations: int) -> float:
        pass
