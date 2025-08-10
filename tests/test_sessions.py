import pytest # Python testing framework
from fastapi.testclient import TestClient # FastAPI testing tool, simulates HTTP requests
from app.main import app # Import the FastAPI app from the main module

client = TestClient(app)

def test_create_session(): # Test POST /sessions endpoint
    response = client.post("/sessions", json={"userId": "testuser"})
    assert response.status_code == 200 # Successful response check
    data = response.json() #Parse JSON response
    assert data["userId"] == "testuser"
    assert data["status"] == "pending"
    assert "sessionId" in data
    assert "desktopUrl" in data
    assert "createdAt" in data

def test_get_session():  # Test GET /sessions endpoint
    create_response = client.post("/sessions", json={"userId": "getuser"}) # Create
    session_id = create_response.json()["sessionId"]

    response = client.get(f"/sessions/{session_id}") # Get Session

    assert response.status_code == 200
    assert response.json()["sessionId"] == session_id
    assert response.json()["status"] == "pending"

def test_terminate_session():  # Test DELETE /sessions/{sessionId} endpoint
    create_response = client.post("/sessions", json={"userId": "deleteuser"})
    session_id = create_response.json()["sessionId"]

    response = client.delete(f"/sessions/{session_id}") # Terminate Session

    assert response.status_code == 200
    assert response.json()["status"] == "terminated"

def test_get_nonexistent_session():  # Test GET /sessions for invalid session ID
    response = client.get("/sessions/fake-session-id")
    assert response.status_code == 404  # Expect 404 Not Found

def test_terminate_nonexistent_session():  # Test DELETE /sessions for invalid session ID
    response = client.delete("/sessions/fake-session-id")
    assert response.status_code == 404  # Expect 404 Not Found

def test_create_session_invalid_payload(): # Test POST /sessions with invalid payload
    response = client.post("/sessions", json={}) #Empty payload
    assert response.status_code == 422  # Expect Unprocessable Entity

def test_empty_session_id_validation(): # Test GET /sessions with empty session ID
    response = client.get("/sessions/ ")
    assert response.status_code == 400
    assert "Session ID cannot be empty" in response.json()["detail"]

def test_delete_empty_session_id(): # Test DELETE /sessions with empty session ID
    response = client.delete("/sessions/ ")
    assert response.status_code == 400
    assert "Session ID cannot be empty" in response.json()["detail"]

def test_error_response_format(): # Test error reponse format
    response = client.get("/sessions/nonexistent")
    assert response.status_code == 404
    error_data = response.json()
    assert "detail" in error_data 

def test_activate_session_success():
    """Test successful activation of pending session"""
    # Create a session first
    create_response = client.post("/sessions", json={"userId": "activateuser"})
    session_id = create_response.json()["sessionId"]
    
    # Activate the session
    response = client.put(f"/sessions/{session_id}/activate")
    
    assert response.status_code == 200
    data = response.json()
    assert data["sessionId"] == session_id
    assert data["status"] == "active"
    assert data["userId"] == "activateuser"

def test_activate_nonexistent_session():
    """Test activating session that doesn't exist returns 404"""
    response = client.put("/sessions/fake-session-id/activate")
    assert response.status_code == 404
    assert "Session not found" in response.json()["detail"]

def test_activate_already_active_session():
    """Test activating already active session returns 409"""
    # Create and activate session
    create_response = client.post("/sessions", json={"userId": "doubleactivate"})
    session_id = create_response.json()["sessionId"]
    client.put(f"/sessions/{session_id}/activate")  # First activation
    
    # Try to activate again
    response = client.put(f"/sessions/{session_id}/activate")
    assert response.status_code == 409
    assert "Cannot activate session in SessionStatus.ACTIVE state" in response.json()["detail"]  # ← Fixed

def test_activate_terminated_session():
    """Test activating terminated session returns 409"""
    # Create, activate, then terminate session
    create_response = client.post("/sessions", json={"userId": "terminateduser"})      
    session_id = create_response.json()["sessionId"]
    client.delete(f"/sessions/{session_id}")  # Terminate

    # Try to activate terminated session
    response = client.put(f"/sessions/{session_id}/activate")
    assert response.status_code == 409
    assert "Cannot activate session in SessionStatus.TERMINATED state" in response.json()["detail"]

def test_activate_empty_session_id():
    """Test activating with empty session ID returns 400"""
    response = client.put("/sessions/ /activate")
    assert response.status_code == 400
    assert "Session ID cannot be empty" in response.json()["detail"]

def test_session_lifecycle_complete():
    """Test complete session lifecycle: create → activate → terminate"""
    # Create
    create_response = client.post("/sessions", json={"userId": "lifecycle"})
    session_id = create_response.json()["sessionId"]
    assert create_response.json()["status"] == "pending"
    
    # Activate
    activate_response = client.put(f"/sessions/{session_id}/activate")
    assert activate_response.json()["status"] == "active"
    
    # Terminate
    terminate_response = client.delete(f"/sessions/{session_id}")
    assert terminate_response.json()["status"] == "terminated"
    
    # Verify final state
    get_response = client.get(f"/sessions/{session_id}")
    assert get_response.json()["status"] == "terminated"