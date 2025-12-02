from pydantic import BaseSettings


class Settings(BaseSettings):
    # You can add env-based configuration here later
    default_difficulty: str = "medium"
    mcts_seed: int | None = None

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
