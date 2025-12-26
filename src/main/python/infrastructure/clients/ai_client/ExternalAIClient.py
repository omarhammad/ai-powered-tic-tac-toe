import httpx
from dataclasses import dataclass

from src.main.python.domain.Mark import Mark


@dataclass
class ExternalAIClient:
    """
    AI client that communicates with the external AI microservice.
    """
    base_url: str
    timeout: float

    def choose_move(self, game_session, difficulty: str):
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

    def winning_proba(self, game_session,for_player: Mark):
        board_raw = game_session.board.get_state()
        board = [v if v is not None else " " for v in board_raw]


        response = httpx.post(
                f"{self.base_url}/winning-proba",
                json={"board": board,"current_player": for_player.value},
                timeout=self.timeout)

        if response.status_code != 200:
                raise Exception(f"AI service error: {response.text}")

        return response.json().get("probability")
