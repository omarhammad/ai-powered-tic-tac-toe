import pytest
from unittest.mock import MagicMock

from domain.GameSession import GameSession
from domain.Mark import Mark


@pytest.fixture
def session():
    logger = MagicMock()
    return GameSession(
        session_id="s1",
        player_x_id="P1",
        player_o_id="P2",
        logger=logger
    )


def test_valid_move_applied():
    s = GameSession("s1", "P1", "P2", logger=MagicMock())
    assert s.make_move(0) is True
    assert s.board.cells[0] == Mark.X


def test_invalid_move_cell_taken():
    s = GameSession("s1", "P1", "P2", logger=MagicMock())
    s.make_move(0)
    assert s.make_move(0) is False


def test_turn_switching():
    s = GameSession("s1", "P1", "P2", logger=MagicMock())

    assert s.current_player.mark == Mark.X
    s.make_move(0)
    assert s.current_player.mark == Mark.O
    s.make_move(1)
    assert s.current_player.mark == Mark.X


def test_win_horizontal():
    s = GameSession("s1", "P1", "P2", logger=MagicMock())
    s.make_move(0)  # X
    s.make_move(3)  # O
    s.make_move(1)  # X
    s.make_move(4)  # O
    s.make_move(2)  # X

    assert s.is_finished
    assert s.winner == Mark.X


def test_win_vertical():
    s = GameSession("s1", "P1", "P2", logger=MagicMock())
    s.make_move(0)
    s.make_move(1)
    s.make_move(3)
    s.make_move(2)
    s.make_move(6)

    assert s.is_finished
    assert s.winner == Mark.X


def test_win_diagonal_main():
    s = GameSession("s1", "P1", "P2", logger=MagicMock())
    s.make_move(0)
    s.make_move(1)
    s.make_move(4)
    s.make_move(2)
    s.make_move(8)

    assert s.is_finished
    assert s.winner == Mark.X


def test_win_diagonal_anti():
    s = GameSession("s1", "P1", "P2", logger=MagicMock())
    s.make_move(2)
    s.make_move(1)
    s.make_move(4)
    s.make_move(3)
    s.make_move(6)

    assert s.is_finished
    assert s.winner == Mark.X


def test_draw_detected():
    s = GameSession("s1", "P1", "P2", logger=MagicMock())

    moves = [0, 1, 2, 4, 3, 5, 7, 6, 8]
    for m in moves:
        s.make_move(m)

    assert s.is_finished
    assert s.winner is None
