from typing import Literal, Optional

from src.main.python.infrastructure.mcts.mcts_agent import choose_move as mcts_choose_move
from src.main.python.domain.TicTacToeState import TicTacToeState
from src.main.python.domain.enums.enums import GameStatus

Difficulty = Literal["easy", "medium", "hard"]


class AIService:
    """
    AI Service responsible for:
    - Taking a TicTacToeState
    - Selecting a move using MCTS (or a simple strategy for "easy")
    - Managing difficulty levels
    - Providing (placeholder) winning probability estimates
    - Stays open to swapping MCTS for ML-based models later.
    """

    def __init__(self):
        # Placeholder current difficulty; could be adapted based on results
        self.current_difficulty: Difficulty = "medium"
        self.human_win_rate: float = 0.5  # placeholder metric

    # ---------------- difficulty handling ----------------

    def _simulations_for_difficulty(self, difficulty: Difficulty) -> int:
        """
        Map difficulty to MCTS computation budget.

        easy   -> few iterations (we'll often use a very simple strategy instead)
        medium -> more simulations
        hard   -> many simulations
        """
        if difficulty == "easy":
            return 50
        if difficulty == "medium":
            return 200
        if difficulty == "hard":
            return 800
        return 200

    def adjust_difficulty(self, human_recent_score: float) -> None:
        """
        Placeholder auto-adjustment:
        - if human is winning a lot (score > 0.7): make it harder
        - if human is losing badly (score < 0.3): make it easier
        - else: keep medium
        """
        self.human_win_rate = human_recent_score

        if human_recent_score > 0.7:
            self.current_difficulty = "hard"
        elif human_recent_score < 0.3:
            self.current_difficulty = "easy"
        else:
            self.current_difficulty = "medium"

    # ---------------- core AI methods ----------------

    def choose_move(
            self,
            state: TicTacToeState,
            difficulty: Optional[Difficulty] = None,
    ) -> int:
        """
        Main API:
        - Takes a TicTacToeState
        - Chooses a move index (0–8) based on difficulty.

        For "easy":
          - Just pick the first legal move (weak but deterministic)
        For "medium"/"hard":
          - Use MCTS with different computation budgets
        """
        if state.is_terminal():
            raise ValueError("Cannot choose move for terminal state.")

        diff: Difficulty = difficulty or self.current_difficulty

        legal_moves = state.legal_moves()
        if not legal_moves:
            raise ValueError("No legal moves available.")

        if diff == "easy":
            # Very simple: first available move
            return legal_moves[0]

        # For medium/hard: call MCTS with different budgets
        sims = self._simulations_for_difficulty(diff)
        return mcts_choose_move(state, computation_budget=sims)

    def get_winning_probability(self, state: TicTacToeState) -> float:
        """
        Placeholder: returns a static probability for now.
        Later:
          - this could call a value network or MCTS-based evaluation.
        """
        if state.status == GameStatus.X_WON or state.status == GameStatus.O_WON:
            return 1.0
        if state.status == GameStatus.DRAW:
            return 0.5

        # For non-terminal states, we just return a static neutral value.
        return 0.5
