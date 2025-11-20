from datetime import datetime

import requests


class LoggingClient:
    """
    Sends gameplay logs to the Java backend via HTTP POST.
    The Service Layer and Domain logic can call this client
    through the LoggingService interface (adapter pattern).
    """

    def __init__(self, base_url: str):
        # Example: "http://localhost:8080/api/logs"
        self.base_url = base_url.rstrip("/")

    def _post(self, endpoint: str, payload: dict):
        """Internal helper to send HTTP POST."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            requests.post(url, json=payload, timeout=2)
        except Exception:
            # Keep it simple: ignore errors for now
            pass

    # -------- LoggingService-compatible methods -------- #

    def log_move(self, session_id: str, player_id: str,
                 board_state, move_index: int, timestamp: datetime):
        payload = {
            "sessionId": session_id,
            "playerId": player_id,
            "boardState": board_state,
            "moveIndex": move_index,
            "timestamp": timestamp.isoformat()
        }
        print(payload)
        self._post("/move", payload)

    def log_state(self, session_id: str, board_state,
                  turn: str, move_count: int, timestamp: datetime):
        payload = {
            "sessionId": session_id,
            "boardState": board_state,
            "turn": turn,
            "moveCount": move_count,
            "timestamp": timestamp.isoformat()
        }
        print(payload)
        self._post("/state", payload)

    def log_end(self, session_id: str, result: str,
                final_board_state, timestamp: datetime):
        payload = {
            "sessionId": session_id,
            "result": result,
            "finalBoardState": final_board_state,
            "timestamp": timestamp.isoformat()
        }
        print(payload)
        self._post("/end", payload)
