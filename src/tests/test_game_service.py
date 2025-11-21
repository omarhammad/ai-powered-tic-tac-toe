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
def logger():
    return MagicMock()


@pytest.fixture
def service(repo, logger):
    return GameService(session_repository=repo, logging_service=logger)


def test_play_move_applies_move(repo, logger):
    """GameService applies a valid human move correctly."""
    p1 = Player("P1", "Omar", Mark.X)
    p2 = Player("P2", "Saif", Mark.O)

    s = GameSession("s1", p1, p2)
    repo.save("s1", s)

    service = GameService(session_repository=repo, logging_service=logger)

    updated = service.apply_move("s1", player_id="P1", move_index=0)

    assert updated.board.cells[0] == Mark.X


def test_play_move_calls_logger(repo, logger):
    """GameService should call logger.log_move() on valid moves."""
    p1 = Player("P1", "Omar", Mark.X)
    p2 = Player("P2", "Saif", Mark.O)

    s = GameSession("s1", p1, p2)
    repo.save("s1", s)

    service = GameService(session_repository=repo, logging_service=logger)

    service.apply_move("s1", player_id="P1", move_index=0)

    assert logger.log_move.called


def test_play_move_returns_updated_session(repo, logger):
    """apply_move() should return the SAME GameSession instance stored in repo."""
    p1 = Player("P1", "Omar", Mark.X)
    p2 = Player("P2", "Saif", Mark.O)

    s = GameSession("s1", p1, p2)
    repo.save("s1", s)

    service = GameService(session_repository=repo, logging_service=logger)

    session_out = service.apply_move("s1", "P1", 0)

    assert session_out is s


def test_invalid_move_does_not_call_logger(repo, logger):
    """Invalid moves should NOT call logger.log_move()."""
    p1 = Player("P1", "Omar", Mark.X)
    p2 = Player("P2", "Saif", Mark.O)

    s = GameSession("s1", p1, p2)
    repo.save("s1", s)

    service = GameService(session_repository=repo, logging_service=logger)

    # First valid move (P1)
    service.apply_move("s1", "P1", 0)

    previous_calls = logger.log_move.call_count

    # P1 tries again – invalid turn order
    with pytest.raises(Exception):
        service.apply_move("s1", "P1", 1)

    assert logger.log_move.call_count == previous_calls
