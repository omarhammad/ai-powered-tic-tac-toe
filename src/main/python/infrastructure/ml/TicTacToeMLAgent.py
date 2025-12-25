from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

import numpy as np
import xgboost as xgb

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
    win_model_path: Optional[str] = None  # intentionally optional

    def __post_init__(self) -> None:
        try:
            # -------------------------------------------------
            # POLICY MODEL (XGBoost Booster)
            # -------------------------------------------------
            self._policy = xgb.Booster()
            self._policy.load_model(self.policy_model_path)

            # -------------------------------------------------
            # WIN MODEL (NOT LOADED YET)
            # -------------------------------------------------
            self._win = None  # placeholder for future use

        except Exception as e:
            raise RuntimeError(
                "Failed to load POLICY model.\n"
                "Ensure:\n"
                "- policy_model_path points to a valid XGBoost .json file\n"
                "- xgboost is installed\n"
            ) from e

    # -------------------------------------------------
    # POLICY MOVE SELECTION (XGBOOST)
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
    # WIN PROBABILITY (DISABLED FOR NOW)
    # -------------------------------------------------

    def winning_probability(self, state: TicTacToeState) -> float:
        raise NotImplementedError(
            "Winning probability model is not loaded yet."
        )

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
