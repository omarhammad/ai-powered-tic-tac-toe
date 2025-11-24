from __future__ import annotations

import math
import random
from typing import List, Optional

from src.main.python.services.mcts.GameState import GameState


class MCTSNode:
    """Single node inside the search tree."""

    def __init__(self, state: GameState, parent: Optional["MCTSNode"] = None, move: Optional[int] = None):
        self.state = state
        self.parent = parent
        self.move = move
        self.children: List[MCTSNode] = []
        self.untried_moves = list(state.legal_moves())
        self.visits = 0
        self.value = 0.0

    def is_fully_expanded(self) -> bool:
        return len(self.untried_moves) == 0

    def expand(self) -> "MCTSNode":
        move = self.untried_moves.pop(random.randrange(len(self.untried_moves)))
        next_state = self.state.next_state(move)
        child = MCTSNode(state=next_state, parent=self, move=move)
        self.children.append(child)
        return child

    def best_child(self, exploration_constant: float, use_exploration: bool = True) -> "MCTSNode":
        best_score = float("-inf")
        best_nodes: List[MCTSNode] = []
        for child in self.children:
            if child.visits == 0:
                score = float("inf")
            else:
                exploit = child.value / child.visits
                if use_exploration:
                    explore = exploration_constant * math.sqrt(math.log(self.visits) / child.visits)
                else:
                    explore = 0.0
                score = exploit + explore

            if score > best_score:
                best_score = score
                best_nodes = [child]
            elif score == best_score:
                best_nodes.append(child)

        return random.choice(best_nodes)
