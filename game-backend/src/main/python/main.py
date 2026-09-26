from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from src.main.python.controllers.GameController import router as game_router

# uvicorn src.main.python.main:app --reload --port 8090
app = FastAPI()

app.mount(
    "/static",
    StaticFiles(directory="src/main/resources/static"),
    name="static"
)

# Include controllers
app.include_router(game_router)


