import pytest
from unittest.mock import MagicMock

from src.main.python.domain.GameSession import GameSession
from src.main.python.domain.Mark import Mark
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
    # Verify that GameService correctly applies a valid move on the board
    s = GameSession("s1", player_x_id="P1", player_o_id="P2")
    repo.save("s1", s)

    service = GameService(session_repository=repo, logging_service=logger)

    updated = service.apply_move("s1", player_id="P1", move_index=0)

    assert updated.board.cells[0] == Mark.X


def test_play_move_calls_logger(repo, logger):
    # Ensure GameService logs a move when a valid move is made
    s = GameSession("s1", player_x_id="P1", player_o_id="P2")
    repo.save("s1", s)

    service = GameService(session_repository=repo, logging_service=logger)

    service.apply_move("s1", player_id="P1", move_index=0)

    assert logger.log_move.called


def test_play_move_returns_updated_session(repo, logger):
    # Check that apply_move returns the same session object from the repo
    s = GameSession("s1", player_x_id="P1", player_o_id="P2")
    repo.save("s1", s)

    service = GameService(session_repository=repo, logging_service=logger)

    session_out = service.apply_move("s1", "P1", 0)

    assert session_out is s


def test_invalid_move_does_not_call_logger(repo, logger):
    # Ensure that invalid moves do NOT cause the logger to be called
    s = GameSession("s1", player_x_id="P1", player_o_id="P2")
    repo.save("s1", s)

    service = GameService(session_repository=repo, logging_service=logger)
    service.apply_move("s1", "P1", 0)

    previous_calls = logger.log_move.call_count

    with pytest.raises(Exception):
        service.apply_move("s1", "P1", 1)  # P1 trying to move twice

    assert logger.log_move.call_count == previous_calls
