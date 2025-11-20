from domain.Mark import Mark


class Player:

    def __init__(self, player_id: str, mark: Mark, is_ai: bool = False):
        self.player_id = player_id
        self.mark = mark
        self.is_ai = is_ai