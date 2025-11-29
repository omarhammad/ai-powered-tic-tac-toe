from typing import Optional
from pydantic import BaseModel


class CreateSessionRequest(BaseModel):
    sessionId: Optional[str] = "3316c4a2-b431-4b19-b9a9-0fe6f424d1ac"
    player_x_id: Optional[str] = "8c5e1f5f-8a62-4483-9cda-9a6c0b4d4bb2"
    player_o_id: Optional[str] = "f3a819f0-2e7f-4fa5-8ebf-1c9f436adf06"
    player_x_name: Optional[str] = "Omar"
    player_o_name: Optional[str] = "Saif"
    playerXIsAI: bool = False
    playerOIsAI: bool = False
    playerXAiType: Optional[str] = None
    playerOAiType: Optional[str] = None
