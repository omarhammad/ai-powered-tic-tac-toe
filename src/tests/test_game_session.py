import pytest
from src.main.python.domain.GameSession import GameSession
from src.main.python.domain.Mark import Mark


@pytest.fixture
def session():
    return GameSession(
        session_id="s1",
        player_x_id="P1",
        player_o_id="P2"
    )


def test_valid_move_applied():
    # Test that a valid move updates the board correctly
    s = GameSession("s1", "P1", "P2")
    assert s.make_move(0) is True
    assert s.board.cells[0] == Mark.X


def test_invalid_move_cell_taken():
    # Ensure that placing a mark in an occupied cell returns False
    s = GameSession("s1", "P1", "P2")
    s.make_move(0)
    assert s.make_move(0) is False


def test_turn_switching():
    # Confirm that turns alternate between X and O after each valid move
    s = GameSession("s1", "P1", "P2")

    assert s.current_player.mark == Mark.X
    s.make_move(0)
    assert s.current_player.mark == Mark.O
    s.make_move(1)
    assert s.current_player.mark == Mark.X


def test_win_horizontal():
    # Validate win detection for horizontal row
    s = GameSession("s1", "P1", "P2")
    s.make_move(0)
    s.make_move(3)
    s.make_move(1)
    s.make_move(4)
    s.make_move(2)

    assert s.is_finished
    assert s.winner == Mark.X


def test_win_vertical():
    # Validate win detection for vertical column
    s = GameSession("s1", "P1", "P2")
    s.make_move(0)
    s.make_move(1)
    s.make_move(3)
    s.make_move(2)
    s.make_move(6)

    assert s.is_finished
    assert s.winner == Mark.X


def test_win_diagonal_main():
    # Validate win detection for main diagonal
    s = GameSession("s1", "P1", "P2")
    s.make_move(0)
    s.make_move(1)
    s.make_move(4)
    s.make_move(2)
    s.make_move(8)

    assert s.is_finished
    assert s.winner == Mark.X


def test_win_diagonal_anti():
    # Validate win detection for anti-diagonal
    s = GameSession("s1", "P1", "P2")
    s.make_move(2)
    s.make_move(1)
    s.make_move(4)
    s.make_move(3)
    s.make_move(6)

    assert s.is_finished
    assert s.winner == Mark.X


def test_draw_detected():
    # Check that a full board with no winner is detected as a draw
    s = GameSession("s1", "P1", "P2")

    moves = [0, 1, 2, 4, 3, 5, 7, 6, 8]
    for m in moves:
        s.make_move(m)

    assert s.is_finished
    assert s.winner is None
