import pytest

from src.main.python.infrastructure.ml.TicTacToeMLAgent import TicTacToeMLAgent
from src.main.python.domain.TicTacToeState import TicTacToeState
from src.main.python.domain.enums.enums import Player


POLICY_MODEL_PATH = "src/main/resources/models/policy_model.json"
WIN_MODEL_PATH = "src/main/resources/models/win_model/artifacts"


def test_choose_move_returns_legal_move():
    agent = TicTacToeMLAgent(
        policy_model_path=POLICY_MODEL_PATH,
        win_model_path=WIN_MODEL_PATH,
    )

    state = TicTacToeState(
        board=[
            "X", "X", " ",
            "O", "O", " ",
            " ", " ", " ",
        ],
        current_player=Player.X,
    )

    move = agent.choose_move(state)

    assert move in state.legal_moves()


def test_winning_probability_returns_valid_range():
    agent = TicTacToeMLAgent(
        policy_model_path=POLICY_MODEL_PATH,
        win_model_path=WIN_MODEL_PATH,
    )

    state = TicTacToeState(
        board=[
            "X", "X", " ",
            "O", "O", " ",
            " ", " ", " ",
        ],
        current_player=Player.X,
    )

    prob = agent.winning_probability(state)

    assert isinstance(prob, float)
    assert 0.0 <= prob <= 1.0
