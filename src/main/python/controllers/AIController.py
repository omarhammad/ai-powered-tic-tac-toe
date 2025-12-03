from typing import Union, Literal

from fastapi import APIRouter

from src.main.python.controllers.dtos.api_models import MoveResponse, TicTacToeStateModel, WinningProbaResponse, \
    ErrorResponse
from src.main.python.domain.enums.enums import Difficulty
from src.main.python.services.AiService import AIService

router = APIRouter()

ai_service = AIService()


@router.post("/choose-move", response_model=Union[MoveResponse, ErrorResponse])
def choose_move(state: TicTacToeStateModel, difficulty: Literal["easy", "medium", "hard"] = "medium"):
    domain_state = state.to_domain()

    if domain_state.is_terminal():
        return ErrorResponse(
            error="Game is already finished. No moves available.",
            status=domain_state.status.value,
        )

    try:
        move_index = ai_service.choose_move(domain_state, difficulty=Difficulty(difficulty))
    except ValueError:
        return ErrorResponse(
            error="Game is already finished. No moves available.",
            status=domain_state.status.value,
        )

    return MoveResponse(index=move_index)


@router.get("/winning-proba", response_model=WinningProbaResponse)
def winning_proba():
    """
    GET /ai/winning-proba

    For now:
      - returns a static probability.
      - later: accept a TicTacToeState and compute real probability.
    """
    # Placeholder: static value
    return WinningProbaResponse(probability=0.5)
