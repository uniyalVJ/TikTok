from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
import uuid

class SessionStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    TERMINATED = "terminated"

class CreateSessionRequest(BaseModel):
    userId: str

class SessionResponse(BaseModel):
    sessionId: str
    userId: str
    status SessionStatus
    desktopUrl: str
    createdAt:datetime

