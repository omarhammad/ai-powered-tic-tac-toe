from typing import Optional

from src.main.python.infrastructure.mcts.mcts_agent import choose_move as mcts_choose_move
from src.main.python.domain.TicTacToeState import TicTacToeState
from src.main.python.domain.enums.enums import GameStatus, Difficulty


class AIService:
    """
    AI Service responsible for:
    - Taking a TicTacToeState
    - Selecting a move using MCTS or a simple strategy (easy)
    - Managing difficulty levels
    - Computing winning probability (placeholder)
    - Future replacement with ML models
    """

    def __init__(self):
        # Default difficulty (can be adjusted over time)
        self.current_difficulty: Difficulty = Difficulty.MEDIUM
        self.human_win_rate: float = 0.5  # placeholder metric

    # ---------------- difficulty handling ----------------

    def _simulations_for_difficulty(self, difficulty: Difficulty) -> int:
        """
        Map Difficulty enum to MCTS computation budget.
        """
        if difficulty == Difficulty.EASY:
            return 100
        if difficulty == Difficulty.MEDIUM:
            return 800
        if difficulty == Difficulty.HARD:
            return 2000
        if difficulty == Difficulty.EXPERT:
            return 8000
        return 800

    def adjust_difficulty(self, human_recent_score: float) -> None:
        """
        Placeholder:
        Auto-adjusts difficulty based on human performance.
        """
        self.human_win_rate = human_recent_score

        if human_recent_score > 0.7:
            self.current_difficulty = Difficulty.HARD
        elif human_recent_score < 0.3:
            self.current_difficulty = Difficulty.EASY
        else:
            self.current_difficulty = Difficulty.MEDIUM

    # ---------------- core AI methods ----------------

    def choose_move(
            self,
            state: TicTacToeState,
            difficulty: Optional[Difficulty] = None,
    ) -> int:
        """
        Main API:
        Chooses the best move based on the selected difficulty.

        EASY   -> simple heuristic (first legal move)
        MEDIUM -> MCTS with medium simulations
        HARD   -> MCTS with high simulations
        """
        if state.is_terminal():
            raise ValueError("Cannot choose move for terminal state.")

        diff: Difficulty = difficulty or self.current_difficulty

        legal_moves = state.legal_moves()
        if not legal_moves:
            raise ValueError("No legal moves available.")

        if diff == Difficulty.EASY:
            # Very simple deterministic move
            return legal_moves[0]

        # For MEDIUM / HARD: run MCTS
        sims = self._simulations_for_difficulty(diff)
        return mcts_choose_move(state, computation_budget=sims)

    def get_winning_probability(self, state: TicTacToeState) -> float:
        """
        Placeholder for ML model integration.
        """
        if state.status in (GameStatus.X_WON, GameStatus.O_WON):
            return 1.0
        if state.status == GameStatus.DRAW:
            return 0.5

        return 0.5
