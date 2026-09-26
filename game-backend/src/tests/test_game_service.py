import pytest
from unittest.mock import MagicMock

from src.main.python.domain.GameSession import GameSession
from src.main.python.domain.Mark import Mark
from src.main.python.domain.Player import Player
from src.main.python.infrastructure.repositories.SessionRepository import SessionRepository
from src.main.python.services.GameService import GameService


@pytest.fixture
def repo():
    return SessionRepository()


@pytest.fixture
def fake_publisher():
    """Mock GameBC publisher."""
    return MagicMock()


@pytest.fixture
def fake_ai():
    """Mock external AI client."""
    fake = MagicMock()
    fake.choose_move.return_value = 4  # AI always returns move index 4
    return fake


@pytest.fixture
def service(repo, fake_publisher, fake_ai):
    return GameService(
        session_repository=repo,
        game_bc_publisher=fake_publisher,
        ai_client=fake_ai,
        default_ai_difficulty="medium",
    )


def test_play_move_applies_move(repo, service):
    """GameService applies a valid human move correctly."""
    p1 = Player("P1", "Omar", Mark.X)
    p2 = Player("P2", "Saif", Mark.O)

    s = GameSession("s1", p1, p2)
    repo.save("s1", s)

    updated = service.apply_move("s1", player_id="P1", move_index=0)

    assert updated.board.cells[0] == Mark.X


def test_play_move_calls_publisher(repo, service, fake_publisher):
    """GameService should publish a GameEvent after a move."""
    p1 = Player("P1", "Omar", Mark.X)
    p2 = Player("P2", "Saif", Mark.O)

    s = GameSession("s1", p1, p2)
    repo.save("s1", s)

    service.apply_move("s1", player_id="P1", move_index=0)

    assert fake_publisher.publish_state.called


def test_play_move_returns_same_session(repo, service):
    """apply_move() returns the SAME GameSession instance."""
    p1 = Player("P1", "Omar", Mark.X)
    p2 = Player("P2", "Saif", Mark.O)

    s = GameSession("s1", p1, p2)
    repo.save("s1", s)

    result = service.apply_move("s1", "P1", 0)

    assert result is s


def test_invalid_move_does_not_call_publisher(repo, service, fake_publisher):
    """Invalid moves must NOT trigger publish_state."""
    p1 = Player("P1", "Omar", Mark.X)
    p2 = Player("P2", "Saif", Mark.O)

    s = GameSession("s1", p1, p2)
    repo.save("s1", s)

    # First move OK
    service.apply_move("s1", "P1", 0)
    prev_calls = fake_publisher.publish_state.call_count

    # Wrong turn → invalid move
    with pytest.raises(Exception):
        service.apply_move("s1", "P1", 1)

    assert fake_publisher.publish_state.call_count == prev_calls
