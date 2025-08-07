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