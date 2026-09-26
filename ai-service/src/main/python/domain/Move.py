from dataclasses import dataclass

from src.main.python.domain.enums.enums import Player


@dataclass
class Move:
    """
    Represents a single move in Tic-Tac-Toe.
    index: 0–8 (flattened 3x3 board)
    player: Player enum ("X" or "O")
    """
    index: int
    player: Player