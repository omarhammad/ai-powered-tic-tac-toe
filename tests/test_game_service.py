import pytest
from unittest.mock import MagicMock

from domain.GameSession import GameSession
from domain.Mark import Mark
from infrastructure.repositories.SessionRepository import SessionRepository
from services.GameService import GameService


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
    s = GameSession("s1", logger=logger)
    repo.save("s1", s)

    service = GameService(session_repository=repo, logging_service=logger)

    updated = service.apply_move("s1", player_id="P1", move_index=0)

    assert updated.board.cells[0] == Mark.X


def test_play_move_calls_logger(repo, logger):
    s = GameSession("s1", logger=logger)
    repo.save("s1", s)

    service = GameService(session_repository=repo, logging_service=logger)

    service.apply_move("s1", player_id="P1", move_index=0)

    # logger.log_move must have been called
    assert logger.log_move.called


def test_play_move_returns_updated_session(repo, logger):
    s = GameSession("s1", logger=logger)
    repo.save("s1", s)

    service = GameService(session_repository=repo, logging_service=logger)

    session_out = service.apply_move("s1", "P1", 0)

    assert session_out is s


def test_invalid_move_does_not_call_logger(repo, logger):
    s = GameSession("s1", logger=logger)
    s.make_move(0)  # X plays
    repo.save("s1", s)

    service = GameService(session_repository=repo, logging_service=logger)

    previous_calls = logger.log_move.call_count
    with pytest.raises(Exception):
        service.apply_move("s1", "P1", 0)  # same cell

    # No logging should occur on invalid moves
    assert logger.log_move.call_count == previous_calls
