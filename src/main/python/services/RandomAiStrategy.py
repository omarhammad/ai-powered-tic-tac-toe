import random

from src.main.python.services.AiStrategy import AiStrategy
from src.main.python.domain.Mark import Mark
from src.main.python.domain.GameSession import GameSession


class RandomAiStrategy(AiStrategy):
    def choose_move(self, game_session: GameSession) -> int:
        """
        Very simple AI:
        - Looks at the board
        - Collects indices of all empty cells
        - Returns a random empty index
        """
        board = game_session.board

        empty_indices = [
            i for i, cell in enumerate(board.cells)
            if cell == Mark.EMPTY
        ]

        if not empty_indices:
            # Should only happen if someone asks for a move
            # in a finished or full game
            raise Exception("RandomAiStrategy: no legal moves available")

        return random.choice(empty_indices)
