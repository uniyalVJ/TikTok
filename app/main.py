from fastapi import FastAPI, HTTPException
from .models import CreateSessionRequest, SessionResponse
from .sessionStore import session_store

app = FastAPI(title="VDI Session Broker", version="1.0.0")


@app.post("/sessions", response_model=SessionResponse) # Tells FastAPI this is a POST endpoint to /sessions
def create_session(request: CreateSessionRequest): # Create a new VDI Session
    session = session_store.create_session(request.userId) # Calls our store to create a new session with UUID
    return session.to_response() # Convert session to API response format JSON

@app.get("/sessions/{session_id}", response_model=SessionResponse) # GET endpoint to retrieve session by ID
def get_session(session_id: str): # Get session by ID
    session = session_store.get_session(session_id) # Retrieve session from store

    if session is None: # If session not found, raise 404 error
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session.to_response()

@app.delete("/sessions/{session_id}", response_model=SessionResponse) # DELETE endpoint to terminate session by ID
def terminate_session(session_id: str): # Terminate session by ID
    session = session_store.terminate_session(session_id) # Change session status to terminated, return updated session

    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session.to_response()


if __name__ == "__main__": # Only run if this file is executed directly
    import uvicorn # ASGI server to run FastAPI app
    uvicorn.run(app, host="0.0.0.0", port=8000) # Run FastAPI app on port 8000