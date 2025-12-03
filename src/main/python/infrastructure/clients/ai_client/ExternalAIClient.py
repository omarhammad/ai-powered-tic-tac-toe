import httpx
from dataclasses import dataclass


@dataclass
class ExternalAIClient:
    """
    AI client that communicates with the external AI microservice.
    """
    base_url: str
    timeout: float

    def choose_move(self, game_session, difficulty: str):
        # Convert None → " " for the external AI service
        board_raw = game_session.board.get_state()
        board = [v if v is not None else " " for v in board_raw]

        current = game_session.current_player.mark.value

        response = httpx.post(
            f"{self.base_url}/choose-move",
            params={"difficulty": difficulty},
            json={"board": board, "current_player": current},
            timeout=self.timeout,
        )

        if response.status_code != 200:
            raise Exception(f"AI service error: {response.text}")

        return response.json()["index"]

    def winning_proba(self, game_session):
        # Convert board to proper string format if needed in the future
        try:
            resp = httpx.get(f"{self.base_url}/winning-proba", timeout=self.timeout)
            if resp.status_code == 200:
                return resp.json().get("probability", 0.5)
        except Exception:
            pass

        return 0.5
