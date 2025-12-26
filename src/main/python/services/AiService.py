from typing import Optional

from src.main.python.infrastructure.mcts.mcts_agent import choose_move as mcts_choose_move
from src.main.python.domain.TicTacToeState import TicTacToeState
from src.main.python.domain.enums.enums import Difficulty
from src.main.python.infrastructure.ml.TicTacToeMLAgent import TicTacToeMLAgent


class AIService:
    _POLICY_MODEL_PATH = "src/main/resources/models/policy_model.json"
    _WIN_MODEL_PATH = "src/main/resources/models/win_model/artifacts"

    def __init__(self):
        self.current_difficulty: Difficulty = Difficulty.MEDIUM
        self.ml_agent = TicTacToeMLAgent(
            policy_model_path=self._POLICY_MODEL_PATH,
            win_model_path=self._WIN_MODEL_PATH
        )

    def _simulations_for_difficulty(self, difficulty: Difficulty) -> int:
        if difficulty == Difficulty.EASY:
            return 200
        if difficulty == Difficulty.MEDIUM:
            return 1500
        if difficulty == Difficulty.HARD:
            return 0
        if difficulty == Difficulty.EXPERT:
            return 20000
        return 800

    def choose_move(
            self,
            state: TicTacToeState,
            difficulty: Optional[Difficulty] = None,
    ) -> int:
        if state.is_terminal():
            raise ValueError("Cannot choose move for terminal state.")

        diff: Difficulty = difficulty or self.current_difficulty
        legal_moves = state.legal_moves()

        if not legal_moves:
            raise ValueError("No legal moves available.")

        if diff == Difficulty.HARD:
            return self.ml_agent.choose_move(state)

        sims = self._simulations_for_difficulty(diff)
        return mcts_choose_move(state, computation_budget=sims)

    def get_winning_probability(self, state: TicTacToeState) -> float:
        return self.ml_agent.winning_probability(state)
