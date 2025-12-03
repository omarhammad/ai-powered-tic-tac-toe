import requests
from src.main.python.domain.GameState import GameState  # adjust import to your structure

class MlLoggingClient:
    """
    Sends ML-oriented GameState logs to the Python Logging microservice via HTTP POST.
    """

    def __init__(self, base_url: str):
        # Example: "http://localhost:9000/api/logs"
        self.base_url = base_url.rstrip("/")

    def _post(self, endpoint: str, payload: dict):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            requests.post(url, json=payload, timeout=2)
        except Exception:
            # Keep it simple: ignore errors for now
            pass

    def log_game_state(self, game_state: GameState):
        """
        Log a single GameState snapshot for ML training.
        """
        payload = game_state.to_dict()
        print("[ML LOG]", payload)
        self._post("/gamestate", payload)
