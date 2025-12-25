import pytest
from fastapi.testclient import TestClient

from src.main.python.main import app

client = TestClient(app)


def is_empty(board, index):
    return board[index] in [" ", None, ""]


def test_choose_move_returns_valid_cell():
    state_json = {
        "board": ["X", "O", " ", " ", "X", " ", "O", " ", " "],
        "current_player": "O",
    }

    resp = client.post("/ai/choose-move?difficulty=medium", json=state_json)
    assert resp.status_code == 200

    idx = resp.json()["index"]

    assert 0 <= idx <= 8
    assert is_empty(state_json["board"], idx)


def test_choose_move_never_picks_filled_cell():
    board = [
        "X", "O", "X",
        "X", "O", "O",
        "O", "X", " "
    ]

    state_json = {"board": board, "current_player": "O"}

    resp = client.post("/ai/choose-move?difficulty=hard", json=state_json)
    assert resp.status_code == 200

    idx = resp.json()["index"]

    # MUST be an empty space
    assert board[idx] == " ", f"AI picked an occupied cell: {idx}"


@pytest.mark.parametrize("difficulty", ["easy", "medium", "hard"])
def test_choose_move_all_difficulties_valid(difficulty):
    state_json = {
        "board": [" "] * 9,
        "current_player": "X",
    }

    resp = client.post(f"/ai/choose-move?difficulty={difficulty}", json=state_json)
    assert resp.status_code == 200

    idx = resp.json()["index"]

    assert 0 <= idx <= 8
    assert is_empty(state_json["board"], idx)


def test_choose_move_terminal_state_rejected():
    # X X X has already won (terminal state)
    state_json = {
        "board": ["X", "X", "X", "O", "O", " ", " ", " ", " "],
        "current_player": "O",
    }

    resp = client.post("/ai/choose-move?difficulty=easy", json=state_json)
    assert resp.status_code == 200

    data = resp.json()
    assert "error" in data
    assert "finished" in data["error"].lower()
