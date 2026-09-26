from dataclasses import field, dataclass
from typing import Optional, Dict

from src.main.python.domain.TicTacToeState import TicTacToeState
from src.main.python.domain.enums.enums import GameStatus


@dataclass
class Node:
    """
    A node in the MCTS tree.
    Holds:
      - state: TicTacToeState
      - parent: parent node
      - children: mapping move_index -> child node
      - visits: number of times visited
      - total_value: accumulated reward
      - untried_moves: moves not yet expanded
    """
    state: TicTacToeState
    parent: Optional["Node"] = None
    move_index: Optional[int] = None  # move leading from parent to this node
    children: Dict[int, "Node"] = field(default_factory=dict)
    visits: int = 0
    total_value: float = 0.0
    untried_moves: list[int] = field(default_factory=list)

    def __post_init__(self):
        if not self.untried_moves and self.state.status == GameStatus.IN_PROGRESS:
            self.untried_moves = self.state.legal_moves()

    def is_fully_expanded(self) -> bool:
        return len(self.untried_moves) == 0

    def is_terminal(self) -> bool:
        return self.state.is_terminal()

