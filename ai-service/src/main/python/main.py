from fastapi import FastAPI
from src.main.python.controllers.AIController import router as ai_router


# uvicorn src.main.python.main:app --reload --port 9100
def create_app() -> FastAPI:
    app = FastAPI(
        title="Tic-Tac-Toe AI Player Service",
        version="1.0.0",
        description="MCTS-based AI player for Tic-Tac-Toe.",
    )

    # All AI endpoints under /ai
    app.include_router(ai_router, prefix="/ai", tags=["tic-tac-toe-ai"])
    return app


app = create_app()
