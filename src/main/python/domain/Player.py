from src.main.python.domain.Mark import Mark


class Player:

    def __init__(self, player_id: str, player_name: str, mark: Mark, is_ai: bool = False):
        self.player_id = player_id
        self.player_name = player_name
        self.mark = mark
        self.is_ai = is_ai
