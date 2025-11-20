from typing import List, Optional

from domain.Mark import Mark


class Board:
    def __init__(self, size: int = 3):
        self.size = size
        self.cells = [Mark.EMPTY] * (size * size)

    def get_state(self) -> List[Optional[str]]:
        return [c.value for c in self.cells]

    def valid_index(self, idx: int) -> bool:
        return 0 <= idx < len(self.cells)

    def is_slot_free(self, idx: int) -> bool:
        return self.cells[idx] == Mark.EMPTY

    def place_mark(self, idx: int, mark: Mark) -> None:
        self.cells[idx] = mark

    def is_full(self) -> bool:
        return all(c != Mark.EMPTY for c in self.cells)