from pydantic import BaseModel, Field #Data validation and settings management using Python type annotations
from datetime import datetime # Track when sessions are created
from enum import Enum # For defining session statuses
import uuid # Generate unique session IDs

class SessionStatus(str, Enum): # Define possible session states
    PENDING = "pending"
    ACTIVE = "active"
    TERMINATED = "terminated"

class CreateSessionRequest(BaseModel): # Validate incoming POST /sessions requests
    userId: str

class SessionResponse(BaseModel): # Standard format for all API responses
    sessionId: str
    userId: str
    status: SessionStatus
    desktopUrl: str
    createdAt: datetime

class Session(BaseModel): # Store sessions in our dictionary
    sessionId: str
    userId: str
    status: SessionStatus = SessionStatus.PENDING # New sessions start as pending
    desktopUrl: str
    createdAt: datetime

    @classmethod
    def create_new(cls, user_id: str) -> "Session":
        session_id = str(uuid.uuid4())
        return cls(
            sessionId=session_id,
            userId=user_id,
            status=SessionStatus.PENDING,
            desktopUrl=f"https://vd-{session_id[:8]}.tiktok.com", # Generate a unique desktop URL with first 8 chars of session ID
            createdAt=datetime.utcnow()
        )
    
    def to_response(self) -> SessionResponse: # Convert session to API response format
        return SessionResponse(
            sessionId=self.sessionId,
            userId=self.userId,
            status=self.status,
            desktopUrl=self.desktopUrl,
            createdAt=self.createdAt
        )