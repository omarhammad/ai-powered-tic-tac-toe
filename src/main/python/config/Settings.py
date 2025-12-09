from pydantic import BaseSettings


class Settings(BaseSettings):
    default_difficulty: str = "medium"
    mcts_seed: int | None = None

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
