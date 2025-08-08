import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from .models import CreateSessionRequest, SessionResponse
from .sessionStore import session_store

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="VDI Session Broker", version="1.0.1")

# Global exception handler for unexpected errors
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled error in {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "detail": str(exc)}
    )

@app.post("/sessions", response_model=SessionResponse) # Tells FastAPI this is a POST endpoint to /sessions
def create_session(request: CreateSessionRequest): # Create a new VDI Session
    try:
        logger.info(f"Creating session for user {request.userId}") # Log the request
        session = session_store.create_session(request.userId) # Calls our store to create a new session with UUID
        return session.to_response() # Convert session to API response format JSON
    except Exception as e: # Catch any unexpected errors
        logger.error(f"Failed to create session  for user {request.userId}: {e}")
        raise HTTPException(status_code=500, detail="Failed to create session") # Return 500 error with message

@app.get("/sessions/{session_id}", response_model=SessionResponse) # GET endpoint to retrieve session by ID
def get_session(session_id: str): # Get session by ID
    
    if not session_id.strip():
        raise HTTPException(status_code=400, detail="Session ID cannot be empty")
    
    session = session_store.get_session(session_id) # Retrieve session from store
    
    if session is None: # If session not found, raise 404 error
        logger.warning(f"Session not found: {session_id}")
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session.to_response()

@app.delete("/sessions/{session_id}", response_model=SessionResponse) # DELETE endpoint to terminate session by ID
def terminate_session(session_id: str): # Terminate session by ID
    
    if not session_id.strip():
        raise HTTPException(status_code=400, detail="Session ID cannot be empty")
    
    session = session_store.terminate_session(session_id) # Change session status to terminated, return updated session

    if session is None:
        logger.warning(f"Session not found for termination: {session_id}")
        raise HTTPException(status_code=404, detail="Session not found")
    
    logger.info(f"Session {session_id} terminated successfully")
    return session.to_response()

@app.get("/health")
def health_check(): # Health check endpoint
    return {
        "status": "healthy", 
        "timestamp": datetime.utcnow() # Return simple health check response
    }


if __name__ == "__main__": # Only run if this file is executed directly
    import uvicorn # ASGI server to run FastAPI app
    uvicorn.run(app, host="0.0.0.0", port=8000) # Run FastAPI app on port 8000