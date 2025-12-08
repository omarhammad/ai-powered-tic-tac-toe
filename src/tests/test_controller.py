from unittest.mock import MagicMock

import pytest
# --- Create a fake FastAPI app for testing only ---
from fastapi import FastAPI
from httpx import ASGITransport, Client

from src.main.python.controllers.GameController import router, get_service_override
from src.main.python.domain.GameSession import GameSession
from src.main.python.domain.Mark import Mark
from src.main.python.domain.Player import Player
from src.main.python.services.GameService import GameService

app = FastAPI()
app.include_router(router)
transport = ASGITransport(app=app)
client = Client(transport=transport, base_url="http://testserver")



# Override dependency for ALL endpoints
@pytest.fixture
def fake_service():
    return MagicMock(spec=GameService)


@pytest.fixture(autouse=True)
def override_service(fake_service):
    app.dependency_overrides[get_service_override] = lambda: fake_service
    yield
    app.dependency_overrides.clear()




# ---------------------------------------------------------
# TEST: /session/create
# ---------------------------------------------------------
def test_create_session_success(fake_service):
    fake_session = GameSession(
        session_id="s1",
        player_x=Player("P1", "Omar", Mark.X, False),
        player_o=Player("P2", "Saif", Mark.O, False)
    )

    fake_service.create_session.return_value = fake_session

    body = {
        "sessionId": "s1",
        "player_x_id": "P1",
        "player_o_id": "P2",
        "player_x_name": "Omar",
        "player_o_name": "Saif",
        "playerXIsAI": False,
        "playerOIsAI": False
    }

    resp = client.post("/session/create", json=body)

    assert resp.status_code == 200
    data = resp.json()

    assert data["sessionId"] == "s1"
    assert len(data["gamePlayableUrls"]) == 2  # both are human


# ---------------------------------------------------------
# TEST: /sessions/{sessionId}
# ---------------------------------------------------------
def test_get_session_state(fake_service):
    fake_session = GameSession(
        session_id="s1",
        player_x=Player("P1", "Omar", Mark.X, False),
        player_o=Player("P2", "Saif", Mark.O, False)
    )

    fake_service.get_session.return_value = fake_session

    resp = client.get("/sessions/s1")

    assert resp.status_code == 200
    data = resp.json()
    assert data["sessionId"] == "s1"
    assert data["isFinished"] is False


def test_get_session_not_found(fake_service):
    fake_service.get_session.return_value = None

    resp = client.get("/sessions/unknown")
    assert resp.status_code == 404


# ---------------------------------------------------------
# TEST: /move
# ---------------------------------------------------------
def test_apply_move_success(fake_service):
    fake_session = MagicMock()
    fake_session.board.get_state.return_value = ["X", None, None, None, None, None, None, None, None]
    fake_session.current_player.mark.value = "O"
    fake_session.is_finished = False
    fake_session.winner = None

    fake_service.apply_move.return_value = fake_session

    body = {
        "sessionId": "s1",
        "playerId": "P1",
        "moveIndex": 0
    }

    resp = client.post("/move", json=body)
    assert resp.status_code == 200

    data = resp.json()
    assert data["isFinished"] is False


def test_apply_move_session_not_found(fake_service):
    fake_service.apply_move.side_effect = ValueError("Session not found")

    body = { "sessionId": "unknown", "playerId": "P1", "moveIndex": 0 }

    resp = client.post("/move", json=body)
    assert resp.status_code == 404


def test_apply_move_error(fake_service):
    fake_service.apply_move.side_effect = Exception("Invalid move")

    body = { "sessionId": "s1", "playerId": "P1", "moveIndex": 99 }

    resp = client.post("/move", json=body)
    assert resp.status_code == 400
