class AiStrategy:
    """
    Only interface. No AI implementation here.
    """
    def choose_move(self, game_session) -> int:
        raise NotImplementedError