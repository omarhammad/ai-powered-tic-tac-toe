from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # RabbitMQ
    AMQP_URL: str = "amqp://user:password@localhost:5671/"
    GAME_EVENTS_EXCHANGE: str = "game.events"
    GAME_EVENTS_ROUTING_KEY: str = "game.tictactoe.state.updated.v1"

    # External AI service
    AI_BASE_URL: str = "http://localhost:8091/ai"
    AI_TIMEOUT: float = 10.0



    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
