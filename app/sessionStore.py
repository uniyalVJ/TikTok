import threading # Lock for thread safety
from typing import Dict, Optional
from .models import Session, SessionStatus

class SessionStore: # Thread-safe in-memoy storage for VDI Sessions

    def __init__(self):
        self._sessions: Dict[str, Session] = {} # Dictionary to store. key=sessionId, value=Session object
        self._lock = threading.Lock() # Ensure thread safety for session access, no race conditions

    def create_session(self, user_id: str) -> Session: # POST - Create a new session & store it
        session = Session.create_new(user_id) # Create a new session

        with self._lock: # Acquire lock before modifying dictionary to ensure thread safety
            self._sessions[session.sessionId] = session # Store session in dictionary using sessionId as key

        return session # Return new session object
    
    def get_session(self, session_id: str) -> Optional[Session]: # GET - Retrieve session by ID
        with self._lock: 
            return self._sessions.get(session_id) # Return session if found, else None

    def terminate_session(self, session_id: str) -> Optional[Session]: # DELETE - Terminate a session by ID, returns updated session or None if session not found
        with self._lock: 
            session = self._sessions.get(session_id) # Get session by ID
            if session is None:
                return None
            
            # Update status directly and store back in dictionary
            session.status = SessionStatus.TERMINATED # Update status to terminated
            self._sessions[session_id] = session # Store updated session back in dictionary
            return session
    
    def session_exists(self, session_id: str) -> bool: # Quick boolean check if session exists
        with self._lock: 
            return session_id in self._sessions
    
    def get_all_sessions(self) -> Dict[str, Session]: # Return copy of entire dictionary for testing/debugging
        with self._lock:
            return self._sessions.copy() # Return a copy to preserve internal state of dictionary, no external modifications
    
    def activate_session(self, session_id: str) -> Optional[Session]:
        with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                return None
        
        if session.status != SessionStatus.PENDING:
            raise ValueError(f"Cannot activate session in {session.status} state")
        
        session.status = SessionStatus.ACTIVE
        self._sessions[session_id] = session
        return session


# Global Instance, shared instance across the application (Singleton pattern)
# FastAPI will import and use this instance
# All sessions live in this one object's dictionary
# Every operation locks before touching the dictionary (Thread Safety)
# Each method completes entirely before releasing lock (ATOMIC)
# Python dictionary in memory, simple and fast

session_store = SessionStore() 