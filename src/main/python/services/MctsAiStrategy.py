from __future__ import annotations

from dataclasses import dataclass

from src.main.python.services.AiStrategy import AiStrategy
from src.main.python.services.mcts.TicTacToeState import TicTacToeState
from src.main.python.services.mcts.search import mcts_best_move


MCTS_DIFFICULTIES = {
    "mcts_easy": 100,
    "mcts_medium": 1000,
    "mcts_hard": 5000,
}


@dataclass
class MctsAiStrategy(AiStrategy):
    """AI strategy wrapper that runs MCTS with a fixed budget per move."""

    simulations: int
    exploration_constant: float = 1.2

    def choose_move(self, game_session) -> int:
        state = TicTacToeState.from_session(game_session)
        return mcts_best_move(state, simulations=self.simulations, exploration_constant=self.exploration_constant)
