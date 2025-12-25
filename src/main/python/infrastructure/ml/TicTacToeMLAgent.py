from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Dict

import numpy as np
import xgboost as xgb
import mlflow.sklearn

from src.main.python.domain.TicTacToeState import TicTacToeState
from src.main.python.domain.enums.enums import Player


# -------------------------------------------------
# FEATURE ENCODING HELPERS
# -------------------------------------------------

def _board_to_encoded(board: List[str]) -> List[int]:
    m = {"X": 1, "O": -1, " ": 0}
    return [m.get(c, 0) for c in board]


def _player_to_encoded(p: Player) -> int:
    return 1 if p == Player.X else -1


def _move_number(board: List[str]) -> int:
    return sum(1 for c in board if c != " ")


# -------------------------------------------------
# ML AGENT
# -------------------------------------------------

@dataclass
class TicTacToeMLAgent:
    policy_model_path: str
    win_model_path: Optional[str] = None

    def __post_init__(self) -> None:
        try:
            # -------------------------------------------------
            # POLICY MODEL (XGBoost)
            # -------------------------------------------------
            self._policy = xgb.Booster()
            self._policy.load_model(self.policy_model_path)

            # -------------------------------------------------
            # WIN MODEL (Sklearn via MLflow)
            # -------------------------------------------------
            self._win = None
            if self.win_model_path:
                self._win = mlflow.sklearn.load_model(self.win_model_path)

        except Exception as e:
            raise RuntimeError(
                "Failed to load ML models.\n"
                "Ensure:\n"
                "- policy_model_path points to a valid XGBoost .json\n"
                "- win_model_path points to MLflow sklearn artifacts\n"
                "- correct Python environment is active\n"
            ) from e

    # -------------------------------------------------
    # POLICY MOVE SELECTION
    # -------------------------------------------------

    def choose_move(self, state: TicTacToeState) -> int:
        legal = state.legal_moves()
        if not legal:
            raise ValueError("No legal moves available.")

        x = self._policy_features(state)
        dmatrix = xgb.DMatrix(x)

        probs = self._policy.predict(dmatrix)[0]
        probs = self._mask_to_legal(probs, legal)

        return int(np.argmax(probs))

    # -------------------------------------------------
    # WIN PROBABILITY
    # -------------------------------------------------

    def winning_probability(self, state: TicTacToeState) -> float:
        if self._win is None:
            raise RuntimeError("WIN model not loaded.")

        x = self._win_features(state)

        probs = self._win.predict_proba(x)[0]
        classes = self._win.classes_

        # class mapping fixed at training time
        label_map = {
            0: "WIN_X",
            1: "WIN_O",
            2: "DRAW",
        }

        prob_map: Dict[str, float] = {
            label_map[c]: float(p)
            for c, p in zip(classes, probs)
        }

        # return probability that CURRENT player wins
        if state.current_player == Player.X:
            return prob_map["WIN_X"]
        else:
            return prob_map["WIN_O"]

    # -------------------------------------------------
    # FEATURE BUILDERS
    # -------------------------------------------------

    def _policy_features(self, state: TicTacToeState) -> np.ndarray:
        feats = _board_to_encoded(state.board) + [
            _player_to_encoded(state.current_player)
        ]
        return np.array(feats, dtype=np.float32).reshape(1, -1)

    def _win_features(self, state: TicTacToeState) -> np.ndarray:
        feats = (
                _board_to_encoded(state.board)
                + [
                    _player_to_encoded(state.current_player),
                    _move_number(state.board),
                ]
        )
        return np.array(feats, dtype=np.float32).reshape(1, -1)

    # -------------------------------------------------
    # LEGAL MOVE MASKING
    # -------------------------------------------------

    def _mask_to_legal(self, probs: np.ndarray, legal: List[int]) -> np.ndarray:
        masked = np.zeros_like(probs, dtype=np.float64)
        masked[legal] = probs[legal]

        s = masked.sum()
        if s <= 0:
            masked[legal] = 1.0 / len(legal)
            return masked

        return masked / s
