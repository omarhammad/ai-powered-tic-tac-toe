from uuid import uuid4

from fastapi import HTTPException, APIRouter, Request, Query
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from src.main.python.controllers.dtos.CreateSessionRequest import CreateSessionRequest
from src.main.python.controllers.dtos.MoveRequest import MoveRequest
from src.main.python.controllers.dtos.MoveResponse import MoveResponse
from src.main.python.domain.GameSession import GameSession
from src.main.python.infrastructure.clients.LoggingClient import LoggingClient
from src.main.python.infrastructure.repositories.SessionRepository import SessionRepository
from src.main.python.services.GameService import GameService

# TODO
#  2) update the player to have name then display that
#  3) update the GameSession , so the logging happens in the GameService - DONE
#  4) update the UI styles to a sketch.
#  5) refine the code and understand better
router = APIRouter()

# Correct paths based on your WORKDIR
templates = Jinja2Templates(directory="src/main/resources/templates")

# Instantiate dependencies

repo = SessionRepository()
logger = LoggingClient(base_url="http://localhost:8080/api/logs")  # Java backend URL
service = GameService(session_repository=repo, logging_service=logger)


# -------------------------------------------------------
# 1. POST /session/create
# -------------------------------------------------------

@router.post("/session/create")
def create_session(req: CreateSessionRequest, request: Request):
    session_id = str(uuid4())

    session: GameSession = service.create_session(
        session_id=session_id,
        player_x_id=req.player_x_id,
        player_o_id=req.player_o_id,
        player_x_name=req.player_x_name,
        player_o_name=req.player_o_name,
        player_x_is_ai=req.playerXIsAI,
        player_o_is_ai=req.playerOIsAI
    )

    base_url = str(request.base_url).rstrip("/")
    return {
        "sessionId": session.session_id,
        "playUrl_X": f"{base_url}/play/{session.session_id}?player_id={session.player_x.player_id}",
        "playUrl_O": f"{base_url}/play/{session.session_id}?player_id={session.player_o.player_id}",

    }


# -------------------------------------------------------
# 2. GET /sessions/{sessionId}  <-- NEW ENDPOINT
# -------------------------------------------------------

@router.get("/sessions/{sessionId}")
def get_session_state(sessionId: str):
    session: GameSession = service.get_session(sessionId)

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
# 3. POST /move
# -------------------------------------------------------

@router.post("/move", response_model=MoveResponse)
def apply_move(req: MoveRequest):
    try:
        session = service.apply_move(
            session_id=req.sessionId,
            player_id=req.playerId,
            move_index=req.moveIndex
        )
    except ValueError:
        raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return MoveResponse(
        board=session.board.get_state(),
        currentTurn=session.current_player.mark.value,  # UPDATED
        isFinished=session.is_finished,
        winner=session.winner.value if session.winner else None
    )


# -------------------------------------------------------
# 4. GET /play/{sessionId}
# -------------------------------------------------------
@router.get("/play/{session_id}", response_class=HTMLResponse)
def serve_ui(request: Request, session_id: str, player_id: str = Query(...)):
    session: GameSession = service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return templates.TemplateResponse(
        "play.html",
        {
            "request": request,
            "sessionId": session.session_id,
            "playerId": player_id
        }
    )
