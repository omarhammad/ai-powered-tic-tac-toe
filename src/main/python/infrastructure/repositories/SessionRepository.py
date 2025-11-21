from typing import Dict, Optional

from src.main.python.domain.GameSession import GameSession


class SessionRepository:
    """
    Stores and retrieves GameSession objects in memory.
    The Service Layer uses this to manage game lifecycle.
    """

    def __init__(self):
        self._sessions: Dict[str, GameSession] = {}

    def save(self, session_id: str, session_obj: GameSession) -> None:
        """Store or replace a GameSession."""
        self._sessions[session_id] = session_obj

    def find(self, session_id: str) -> Optional[GameSession]:
        """Retrieve a GameSession by ID."""
        return self._sessions.get(session_id)

    def exists(self, session_id: str) -> bool:
        return session_id in self._sessions
