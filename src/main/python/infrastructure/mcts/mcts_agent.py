import math
import random
from typing import Optional

from src.main.python.domain.TicTacToeState import TicTacToeState
from src.main.python.domain.enums.enums import Player, GameStatus
from src.main.python.infrastructure.mcts.mcts_node import Node


class MCTS:
    """
    Monte Carlo Tree Search for Tic-Tac-Toe.

    Steps:
      1) Selection: walk down the tree using UCB1 until a node with untried moves or terminal.
      2) Expansion: expand one new child.
      3) Simulation: play random moves until terminal state.
      4) Backpropagation: propagate result up the tree.
    """

    def __init__(self, seed: int = 42):
        # Deterministic random generator for reproducible behavior
        self.random = random.Random(seed)
        self.root_player: Optional[Player] = None

    def search(self, root_state: TicTacToeState, iterations: int) -> int:
        """
        Run MCTS for a number of iterations and return the best move index.
        """
        if root_state.is_terminal():
            raise ValueError("Cannot run MCTS on terminal state.")

        self.root_player = root_state.current_player
        root = Node(state=root_state)

        for _ in range(iterations):
            leaf = self._select(root)
            reward = self._simulate(leaf.state)
            self._backpropagate(leaf, reward)

        if not root.children:
            # No moves found (should not happen if state is not terminal)
            raise RuntimeError("MCTS failed to expand any moves.")

        # Choose child with highest visit count
        best_move, best_child = max(
            root.children.items(),
            key=lambda item: item[1].visits,
        )
        return best_move

    # -------------------- core steps --------------------

    def _select(self, node: Node) -> Node:
        """
        Selection:
        - while node is fully expanded and non-terminal, move to best UCB1 child
        - otherwise return node (to expand or simulate)
        """
        while not node.is_terminal():
            if node.untried_moves:
                return self._expand(node)
            node = self._best_ucb1_child(node)
        return node

    def _expand(self, node: Node) -> Node:
        """
        Expansion:
        - pick one untried move (deterministically smallest index)
        - create child node for that move
        """
        move_index = min(node.untried_moves)
        node.untried_moves.remove(move_index)

        new_state = node.state.apply_move(move_index)
        child = Node(state=new_state, parent=node, move_index=move_index)
        node.children[move_index] = child
        return child

    def _best_ucb1_child(self, node: Node, c_param: float = 1.4) -> Node:
        """
        Select child with maximum UCB1 score:
          Q / N + c * sqrt(ln(N_parent) / N)
        """
        best_score = float("-inf")
        best_child: Optional[Node] = None

        for child in node.children.values():
            if child.visits == 0:
                score = float("inf")
            else:
                exploit = child.total_value / child.visits
                explore = c_param * math.sqrt(math.log(node.visits) / child.visits)
                score = exploit + explore

            if score > best_score:
                best_score = score
                best_child = child

        if best_child is None:
            raise RuntimeError("No best child found during selection.")

        return best_child

    def _simulate(self, state: TicTacToeState, max_depth: int = 20) -> float:
        """
        Simulation:
        - From the given state, play random moves until terminal or max_depth.
        - Return reward from root player's perspective:
            1.0 for win, 0.0 for loss, 0.5 for draw / non-terminal.
        """
        current = state
        depth = 0

        while not current.is_terminal() and depth < max_depth:
            moves = current.legal_moves()
            if not moves:
                break
            move = self.random.choice(moves)
            current = current.apply_move(move)
            depth += 1

        winner = current.winner()
        if winner is None:
            # Draw or non-terminal cutoff
            if current.status == GameStatus.DRAW:
                return 0.5
            return 0.5

        if winner == self.root_player:
            return 1.0
        return 0.0

    def _backpropagate(self, node: Node, reward: float) -> None:
        """
        Backpropagation:
        - Walk up from leaf to root, updating visits and total_value.
        """
        current = node
        while current is not None:
            current.visits += 1
            current.total_value += reward
            current = current.parent


# -------------------------------------------------------------------
# Convenience function used by higher layers
# -------------------------------------------------------------------

def choose_move(state: TicTacToeState, computation_budget: int, seed: int = 42) -> int:
    """
    Convenience function:
      - creates an MCTS instance
      - runs search
      - returns best move index
    """
    mcts = MCTS(seed=seed)
    return mcts.search(root_state=state, iterations=computation_budget)