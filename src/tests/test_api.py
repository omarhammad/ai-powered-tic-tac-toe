import pytest
from fastapi.testclient import TestClient

from src.main.python.main import app

client = TestClient(app)


def test_choose_move_returns_valid_cell():
    """
    /ai/choose-move should return a legal move index (0–8) on a non-terminal board.
    """
    state_json = {
        "board": ["X", "O", " ", " ", "X", " ", "O", " ", " "],
        "current_player": "O"
    }

    resp = client.post("/ai/choose-move?difficulty=medium", json=state_json)
    assert resp.status_code == 200

    data = resp.json()
    idx = data["index"]

    # Compute row/col locally (API doesn't send them anymore)
    row, col = divmod(idx, 3)

    # Basic checks
    assert 0 <= idx <= 8
    assert 0 <= row <= 2
    assert 0 <= col <= 2

    # Ensure move was on an empty cell
    assert state_json["board"][idx] == " "


def test_choose_move_changes_with_difficulty():
    """
    /ai/choose-move must accept difficulty and still return legal moves.
    """
    state_json = {
        "board": [" ", " ", " ", " ", " ", " ", " ", " ", " "],
        "current_player": "X"
    }

    resp_easy = client.post("/ai/choose-move?difficulty=easy", json=state_json)
    resp_hard = client.post("/ai/choose-move?difficulty=hard", json=state_json)

    assert resp_easy.status_code == 200
    assert resp_hard.status_code == 200

    move_easy = resp_easy.json()["index"]
    move_hard = resp_hard.json()["index"]

    assert 0 <= move_easy <= 8
    assert 0 <= move_hard <= 8


def test_winning_proba_endpoint_exists():
    """
    /ai/winning-proba should exist and return a JSON with 'probability'.
    """
    resp = client.get("/ai/winning-proba")
    assert resp.status_code == 200

    data = resp.json()
    assert "probability" in data
    assert isinstance(data["probability"], (int, float))
