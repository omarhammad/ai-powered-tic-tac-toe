from __future__ import annotations

import random
from typing import Optional

from src.main.python.domain.Mark import Mark
from src.main.python.services.mcts.GameState import GameState
from src.main.python.services.mcts.MCTSNode import MCTSNode


def mcts_best_move(state: GameState, simulations: int, exploration_constant: float = 1.4) -> int:
    """Run MCTS starting from the provided state and return the best move."""
    root_player = state.current_player()
    root = MCTSNode(state)

    if not root.untried_moves and not root.children and state.is_terminal():
        raise ValueError("Cannot run MCTS on a finished game")

    for _ in range(max(simulations, 1)):
        node = root
        # Selection
        while not node.state.is_terminal() and node.is_fully_expanded() and node.children:
            node = node.best_child(exploration_constant)

        # Expansion
        if not node.state.is_terminal() and node.untried_moves:
            node = node.expand()

        # Simulation
        reward = rollout(node.state, root_player)

        # Backpropagation
        while node is not None:
            node.visits += 1
            node.value += reward
            node = node.parent

    best_node = root.best_child(exploration_constant=0.0, use_exploration=False)
    return best_node.move  # type: ignore[return-value]


def rollout(state: GameState, perspective_player: Mark) -> float:
    current_state = state
    while not current_state.is_terminal():
        moves = current_state.legal_moves()
        if not moves:
            break
        move = random.choice(moves)
        current_state = current_state.next_state(move)

    return current_state.result(perspective_player)
