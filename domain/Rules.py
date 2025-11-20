from typing import Optional

from domain.Board import Board
from domain.Mark import Mark


class Rules:
    def __init__(self, size: int = 3):
        self.size = size
        self.winning_lines = self._lines()

    def _lines(self):
        s = self.size
        lines = []

        # rows
        for r in range(s):
            lines.append([r * s + i for i in range(s)])

        # cols
        for c in range(s):
            lines.append([c + s * i for i in range(s)])

        # diags
        lines.append([i * (s + 1) for i in range(s)])
        lines.append([(i + 1) * (s - 1) for i in range(s)])

        return lines

    def check_winner(self, board: Board) -> Optional[Mark]:
        cells = board.cells
        for line in self.winning_lines:
            marks = [cells[i] for i in line]
            if marks[0] != Mark.EMPTY and all(m == marks[0] for m in marks):
                return marks[0]
        return None

    def is_draw(self, board: Board) -> bool:
        return board.is_full() and self.check_winner(board) is None
