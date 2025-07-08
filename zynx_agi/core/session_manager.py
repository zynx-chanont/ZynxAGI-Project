from typing import Dict, Any, Optional
from uuid import uuid4

class Session:
    """Represents a user session."""
    def __init__(self, session_id: str):
        self.session_id: str = session_id
        self.created_at: float = time.time() # type: ignore
        self.last_accessed: float = time.time() # type: ignore
        self.data: Dict[str, Any] = {}

    def get(self, key: str) -> Optional[Any]:
        self.last_accessed = time.time() # type: ignore
        return self.data.get(key)

    def set(self, key: str, value: Any) -> None:
        self.last_accessed = time.time() # type: ignore
        self.data[key] = value

    def update_data(self, data: Dict[str, Any]) -> None:
        self.last_accessed = time.time() # type: ignore
        self.data.update(data)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "last_accessed": self.last_accessed,
            "data": self.data,
        }

class SessionManager:
    """Manages user sessions (in-memory for now)."""
    def __init__(self):
        self._sessions: Dict[str, Session] = {}

    def create_session(self) -> Session:
        session_id = str(uuid4())
        session = Session(session_id)
        self._sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        session = self._sessions.get(session_id)
        if session:
            session.last_accessed = time.time() # type: ignore
        return session

    def delete_session(self, session_id: str) -> bool:
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False

    def get_all_sessions(self) -> list[Session]:
        return list(self._sessions.values())

# Placeholder for time import, will be added if not present by other logic
import time
