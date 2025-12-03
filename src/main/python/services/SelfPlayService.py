import uuid
import random
from typing import Tuple

from src.main.python.domain.TicTacToeState import TicTacToeState
from src.main.python.domain.GameState import GameState
from src.main.python.domain.enums.enums import Player, GameStatus, Difficulty
from src.main.python.services.AiService import AIService
from src.main.python.infrastructure.logging.LoggingClient import LoggingClient


class SelfPlayService:
    """
    Runs AI vs AI self-play games and logs every move.
    """

    def __init__(
            self,
            ai_service: AIService,
            logging_client: LoggingClient,
            exploration_noise: float = 0.15,
    ):
        self.ai_service = ai_service
        self.logger = logging_client
        self.noise = exploration_noise

    # ---------------------------------------------------------
    # Main entry point
    # ---------------------------------------------------------
    def generate_self_play_dataset(self, num_games: int):
        for _ in range(num_games):
            self._run_single_game()

    # ---------------------------------------------------------
    # Run one self-play game
    # ---------------------------------------------------------
    def _run_single_game(self):
        game_session_id = str(uuid.uuid4())
        state = TicTacToeState()

        diff_x, diff_o = self._random_agent_difficulties()
        move_number = 0

        while True:

            current_player: Player = state.current_player
            legal_moves = state.legal_moves()

            # Terminal BEFORE move
            if state.is_terminal():
                break

            # Pick difficulty based on player
            current_diff = diff_x if current_player == Player.X else diff_o

            # 1. Exploit move
            chosen_move = self.ai_service.choose_move(
                state,
                difficulty=current_diff
            )

            # 2. Strong MCTS best move
            best_move = self.ai_service.choose_move(
                state,
                difficulty=Difficulty.EXPERT
            )

            # 3. Exploration noise
            noisy_move = self._apply_exploration_noise(state, chosen_move)

            # ---- Build GameState BEFORE applying move ----
            gs = GameState(
                game_session_id=game_session_id,
                move_number=move_number,
                board_state=state.board.copy(),
                current_player=current_player,
                legal_moves=legal_moves,
                action_taken=noisy_move,
                best_move_strong=best_move,
                outcome=GameStatus.IN_PROGRESS,
                reward=0.0,
                difficulty=current_diff,
            )

            # ---- Apply move ----
            next_state = state.apply_move(noisy_move)

            # ---- Check if move ended the game ----
            if next_state.is_terminal():
                final_outcome = next_state.status
                final_reward = self._reward_from_outcome(final_outcome)

                # Rebuild terminal GameState with final outcome & reward
                terminal_gs = GameState(
                    game_session_id=game_session_id,
                    move_number=move_number,
                    board_state=state.board.copy(),
                    current_player=current_player,
                    legal_moves=legal_moves,
                    action_taken=noisy_move,
                    best_move_strong=best_move,
                    outcome=final_outcome,
                    reward=final_reward,
                    difficulty=current_diff,
                )

                # Log the terminal state
                self.logger.log_game_state(terminal_gs.to_dict())
                break

            # ---- If not terminal, log normally ----
            self.logger.log_game_state(gs.to_dict())

            # Continue the game
            state = next_state
            move_number += 1

    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------
    def _random_agent_difficulties(self) -> Tuple[Difficulty, Difficulty]:
        diffs = [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]
        return random.choice(diffs), random.choice(diffs)

    def _apply_exploration_noise(self, state: TicTacToeState, move: int) -> int:
        if random.random() < self.noise:
            return random.choice(state.legal_moves())
        return move

    def _reward_from_outcome(self, outcome: GameStatus) -> float:
        if outcome == GameStatus.X_WON:
            return 1.0
        if outcome == GameStatus.O_WON:
            return -1.0
        return 0.0
