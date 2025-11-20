from uuid import uuid4

from fastapi import HTTPException, APIRouter
from starlette.responses import HTMLResponse

from controllers.dtos.CreateSessionRequest import CreateSessionRequest
from controllers.dtos.MoveRequest import MoveRequest
from controllers.dtos.MoveResponse import MoveResponse
from domain.GameSession import GameSession
from infrastructure.clients.LoggingClient import LoggingClient
from infrastructure.repositories.SessionRepository import SessionRepository
from services.GameService import GameService

router = APIRouter()
# Instantiate dependencies

repo = SessionRepository()
logger = LoggingClient(base_url="http://localhost:8080/api/logs")  # Java backend URL
service = GameService(session_repository=repo, logging_service=logger)


# -------------------------------------------------------
# 1. POST /session/create
# -------------------------------------------------------

@router.post("/session/create")
def create_session(req: CreateSessionRequest):
    session_id = str(uuid4())

    session : GameSession = service.create_session(
        session_id=session_id,
        player_x=req.playerX,
        player_o=req.playerO,
        player_x_is_ai=req.playerXIsAI,
        player_o_is_ai=req.playerOIsAI
    )

    return {
        "sessionId": session.session_id,
        "playUrl": f"/play/{session.session_id}"
    }


# -------------------------------------------------------
# 2. POST /move
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
        currentTurn=session.current_player.mark.value,        # UPDATED
        isFinished=session.is_finished,
        winner=session.winner.value if session.winner else None
    )


# -------------------------------------------------------
# 3. GET /play/{sessionId}
# -------------------------------------------------------

@router.get("/play/{sessionId}", response_class=HTMLResponse)
def serve_ui(sessionId: str):
    """
    Returns the HTML UI for the game.
    In real projects you would load a template file.
    Keeping it simple here.
    """
    if not service.get_session(sessionId):
        raise HTTPException(status_code=404, detail="Session not found")

    html = f"""
    <html>
    <head><title>Play Tic-Tac-Toe</title></head>
    <body>
        <h1>Tic-Tac-Toe</h1>
        <div id="app">Loading game {sessionId}...</div>

        <script>
            const sessionId = "{sessionId}";
            // Frontend JS app would mount here
        </script>
    </body>
    </html>
    """
    return html
