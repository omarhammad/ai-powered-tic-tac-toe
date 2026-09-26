import pytest

from src.main.python.domain.GameSession import GameSession
from src.main.python.domain.Mark import Mark
from src.main.python.domain.Player import Player


@pytest.fixture
def session():
    """Create a basic GameSession with 2 human players."""
    p1 = Player("P1", "PlayerX", Mark.X)
    p2 = Player("P2", "PlayerO", Mark.O)
    return GameSession(session_id="s1", player_x=p1, player_o=p2)


def test_valid_move_applied():
    """A valid move should place the correct mark on the board."""
    p1 = Player("P1", "X_Player", Mark.X)
    p2 = Player("P2", "O_Player", Mark.O)

    s = GameSession("s1", p1, p2)

    assert s.make_move(0) is True
    assert s.board.cells[0] == Mark.X


def test_invalid_move_cell_taken():
    """Attempting to play in an occupied cell should fail."""
    p1 = Player("P1", "X", Mark.X)
    p2 = Player("P2", "O", Mark.O)

    s = GameSession("s1", p1, p2)

    s.make_move(0)  # X plays
    assert s.make_move(0) is False  # X cannot play again in the same spot


def test_turn_switching():
    """Turns must alternate between X and O after each valid move."""
    p1 = Player("P1", "X", Mark.X)
    p2 = Player("P2", "O", Mark.O)

    s = GameSession("s1", p1, p2)

    assert s.current_player.mark == Mark.X
    s.make_move(0)
    assert s.current_player.mark == Mark.O
    s.make_move(1)
    assert s.current_player.mark == Mark.X


def test_win_horizontal():
    """X wins with the first horizontal row."""
    p1 = Player("P1", "X", Mark.X)
    p2 = Player("P2", "O", Mark.O)

    s = GameSession("s1", p1, p2)
    s.make_move(0)  # X
    s.make_move(3)  # O
    s.make_move(1)  # X
    s.make_move(4)  # O
    s.make_move(2)  # X wins

    assert s.is_finished
    assert s.winner == Mark.X


def test_win_vertical():
    """X wins with the first vertical column."""
    p1 = Player("P1", "X", Mark.X)
    p2 = Player("P2", "O", Mark.O)

    s = GameSession("s1", p1, p2)
    s.make_move(0)  # X
    s.make_move(1)  # O
    s.make_move(3)  # X
    s.make_move(2)  # O
    s.make_move(6)  # X wins

    assert s.is_finished
    assert s.winner == Mark.X


def test_win_diagonal_main():
    """X wins using the main diagonal."""
    p1 = Player("P1", "X", Mark.X)
    p2 = Player("P2", "O", Mark.O)

    s = GameSession("s1", p1, p2)
    s.make_move(0)  # X
    s.make_move(1)  # O
    s.make_move(4)  # X
    s.make_move(2)  # O
    s.make_move(8)  # X wins

    assert s.is_finished
    assert s.winner == Mark.X


def test_win_diagonal_anti():
    """X wins using the anti-diagonal."""
    p1 = Player("P1", "X", Mark.X)
    p2 = Player("P2", "O", Mark.O)

    s = GameSession("s1", p1, p2)
    s.make_move(2)  # X
    s.make_move(1)  # O
    s.make_move(4)  # X
    s.make_move(3)  # O
    s.make_move(6)  # X wins

    assert s.is_finished
    assert s.winner == Mark.X


def test_draw_detected():
    """A full board with no winner should be marked as a draw."""
    p1 = Player("P1", "X", Mark.X)
    p2 = Player("P2", "O", Mark.O)

    s = GameSession("s1", p1, p2)

    moves = [0, 1, 2, 4, 3, 5, 7, 6, 8]  # fill the board: draw
    for m in moves:
        s.make_move(m)

    assert s.is_finished
    assert s.winner is None
