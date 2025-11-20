from datetime import datetime
from typing import List, Optional



class LoggingService:
    def log_move(self, session_id: str, player_id: str,
                 board_state: List[Optional[str]], move_index: int,
                 timestamp: datetime):
        raise NotImplementedError

    def log_state(self, session_id: str, board_state: List[Optional[str]],
                  turn: str, move_count: int, timestamp: datetime):
        raise NotImplementedError

    def log_end(self, session_id: str, result: str,
                final_board_state: List[Optional[str]], timestamp: datetime):
        raise NotImplementedError
