from src.main.python.domain.TicTacToeState import TicTacToeState
from src.main.python.infrastructure.AIModels import AIModel


class PlaceholderModel(AIModel):
    """
    Skeleton ML model to be implemented later.
    """

    def choose_move(self, state: TicTacToeState, simulations: int) -> int:
        raise NotImplementedError("ML model not implemented yet.")

    def winning_probability(self, state: TicTacToeState, simulations: int) -> float:
        raise NotImplementedError("ML model not implemented yet.")
