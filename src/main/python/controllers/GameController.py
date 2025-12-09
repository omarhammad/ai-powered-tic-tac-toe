from fastapi import HTTPException, APIRouter, Request, Query, Depends
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from src.main.python.config.config import settings
from src.main.python.controllers.dtos.CreateSessionRequest import CreateSessionRequest
from src.main.python.controllers.dtos.MoveRequest import MoveRequest
from src.main.python.controllers.dtos.MoveResponse import MoveResponse
from src.main.python.domain.GameSession import GameSession
from src.main.python.infrastructure.messaging.GameBcPublisher import GameBcPublisher
from src.main.python.infrastructure.repositories.SessionRepository import SessionRepository
from src.main.python.services.GameService import GameService
from src.main.python.infrastructure.clients.ai_client.ExternalAIClient import ExternalAIClient

router = APIRouter()
templates = Jinja2Templates(directory="src/main/resources/templates")

repo = SessionRepository()

game_bc_publisher = GameBcPublisher(
    amqp_url=settings.AMQP_URL,
    exchange=settings.GAME_EVENTS_EXCHANGE,
    routing_key=settings.GAME_EVENTS_ROUTING_KEY,
)

ai_client = ExternalAIClient(
    base_url=settings.AI_BASE_URL,
    timeout=settings.AI_TIMEOUT
)


def get_service_override():
    return GameService(
        session_repository=repo,
        game_bc_publisher=game_bc_publisher,
        ai_client=ai_client,
        default_ai_difficulty="medium",
    )


# -------------------------------------------------------
# CREATE SESSION
# -------------------------------------------------------
@router.post("/session/create")
def create_session(req: CreateSessionRequest, request: Request, svc: GameService = Depends(get_service_override)):
    if req.playerXIsAI and req.playerOIsAI:
        raise HTTPException(
            status_code=400,
            detail="AI vs AI is not supported"
        )

    try:
        session: GameSession = svc.create_session(
            session_id=req.sessionId,
            player_x_id=req.player_x_id,
            player_o_id=req.player_o_id,
            player_x_name=req.player_x_name,
            player_o_name=req.player_o_name,
            player_x_is_ai=req.playerXIsAI,
            player_o_is_ai=req.playerOIsAI,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    base_url = str(request.base_url).rstrip("/")
    urls = []

    # Only HUMAN players get playable URLs
    for player in (session.player_x, session.player_o):
        if not player.is_ai:
            urls.append(f"{base_url}/play/{session.session_id}?player_id={player.player_id}")

    return {
        "sessionId": session.session_id,
        "gamePlayableUrls": urls
    }


# -------------------------------------------------------
# GET SESSION STATE
# -------------------------------------------------------
@router.get("/sessions/{sessionId}")
def get_session_state(sessionId: str, svc: GameService = Depends(get_service_override)):
    session: GameSession = svc.get_session(sessionId)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "sessionId": session.session_id,
        "board": session.board.get_state(),
        "currentTurn": session.current_player.mark.value,
        "playerX": {
            "id": session.player_x.player_id,
            "name": session.player_x.player_name,
            "isAI": session.player_x.is_ai
        },
        "playerO": {
            "id": session.player_o.player_id,
            "name": session.player_o.player_name,
            "isAI": session.player_o.is_ai
        },
        "isFinished": session.is_finished,
        "winner": session.winner.value if session.winner else None
    }


# -------------------------------------------------------
# APPLY MOVE
# -------------------------------------------------------
@router.post("/move", response_model=MoveResponse)
def apply_move(req: MoveRequest, svc: GameService = Depends(get_service_override)):
    try:
        session = svc.apply_move(
            session_id=req.sessionId,
            player_id=req.playerId,
            move_index=req.moveIndex,
        )
    except ValueError:
        raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return MoveResponse(
        board=session.board.get_state(),
        currentTurn=session.current_player.mark.value,
        isFinished=session.is_finished,
        winner=session.winner.value if session.winner else None
    )


# -------------------------------------------------------
# SERVE UI
# -------------------------------------------------------
@router.get("/play/{session_id}", response_class=HTMLResponse)
def serve_ui(request: Request, session_id: str, player_id: str = Query(...),
             svc: GameService = Depends(get_service_override)):
    session: GameSession = svc.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if not (session.player_x.player_id == player_id or session.player_o.player_id == player_id):
        raise HTTPException(status_code=404, detail="Player not found, maybe wrong session")

    return templates.TemplateResponse(
        "play.html",
        {
            "request": request,
            "sessionId": session.session_id,
            "playerId": player_id
        }
    )


__all__ = ["router"]
