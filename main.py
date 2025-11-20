from fastapi import FastAPI
from controllers.GameController import router as game_router

app = FastAPI()

# Include controllers
app.include_router(game_router)
