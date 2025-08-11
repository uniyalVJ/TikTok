# VDI Session Broker

A containerized microservice that acts as a "Session Broker" for VDI (Virtual Desktop Infrastructure) platforms. This service provides a RESTful API to manage user sessions with support for creating, retrieving, activating, and terminating VDI sessions.

## Table of Contents

- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Development Setup](#development-setup)
- [Testing Guide](#testing-guide)
- [API Documentation](#api-documentation)
- [Container Operations](#container-operations)
- [Debugging & Troubleshooting](#debugging--troubleshooting)
- [CI/CD Pipeline](#cicd-pipeline)


## Architecture

```
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI application and endpoints
│   ├── models.py         # Pydantic models and session data structures
│   └── sessionStore.py   # Thread-safe in-memory session storage
├── tests/
│   ├── __init__.py
│   └── test_sessions.py  # Comprehensive test suite
├── .github/workflows/
│   └── cicd.yml         # CI/CD pipeline configuration
├── Dockerfile           # Multi-stage container build
├── requirements.txt     # Python dependencies
└── README.md            # README instructions (this file)
```

## Quick Start

### 1. Build and Run Container

```bash
# Build the container
docker build -t vdi-session-broker .

# Run container and map port 8000
docker run -p 8000:8000 vdi-session-broker

# Check if container is running
docker ps | grep vdi-session-broker
```

### 2. Test Basic Functionality

```bash
# Test health endpoint
curl http://localhost:8000/health

# Create a session
curl -X POST "http://localhost:8000/sessions" \
     -H "Content-Type: application/json" \
     -d '{"userId": "quicktest"}'

# Save the sessionId from the response above, then test retrieval
curl -X GET "http://localhost:8000/sessions/YOUR_SESSION_ID"

# Delete the session using same ID
curl -X DELETE "http://localhost:8000/sessions/YOUR_SESSION_ID"


```

### 3. Interactive API Testing

Open your browser to: **http://localhost:8000/docs**

This provides a complete interactive API interface where you can test all endpoints.


### 4. Cleanup

```bash

# Cleanup
docker stop test-session-broker && docker rm test-session-broker

```
## Development Setup

### Prerequisites

- Python 3.11+
- Docker
- Git


### Local Development

```bash
# Install dependencies (includes uvicorn)
pip install -r requirements.txt

# Run with auto-reload for development
uvicorn app.main:app --reload --log-level info

# Application will be available at: http://localhost:8000
# Interactive docs at: http://localhost:8000/docs

```

## Testing Guide

### 1. Run Unit Tests

```bash
# Run all tests with verbose output
pytest tests/ -v

```

## API Documentation

### Endpoints Overview

| Method | Endpoint | Description | Status Codes |
|--------|----------|-------------|--------------|
| POST | `/sessions` | Create new session | 200, 422, 500 |
| GET | `/sessions/{sessionId}` | Get session status | 200, 400, 404 |
| PUT | `/sessions/{sessionId}/activate` | Activate session | 200, 400, 404, 409 |
| DELETE | `/sessions/{sessionId}` | Terminate session | 200, 400, 404 |
| GET | `/health` | Health check | 200 |

#### Error Testing

```bash
# Test invalid session ID
curl -X GET "http://localhost:8000/sessions/invalid-id"
# Expected: 404 Not Found -> {"detail":"Session not found"}

# Test empty session ID
curl -X GET "http://localhost:8000/sessions/%20"
# Expected: 400 Bad Request -> {"detail":"Session ID cannot be empty"}

# Test invalid payload
curl -X POST "http://localhost:8000/sessions" \
     -H "Content-Type: application/json" \
     -d '{}'
# Expected: 422 Unprocessable Entity -> {"detail":[{"type":"missing","loc":["body","userId"],"msg":"Field required","input":{}}]}

# Test activating already active session
curl -X PUT "http://localhost:8000/sessions/YOUR_SESSION_ID/activate"
# (after already activating)
# Expected: 409 Conflict -> {"detail":"Cannot activate session in SessionStatus.ACTIVE state"}
```

## Container Operations

### Container Inspection

```bash
# Check image size
docker images vdi-session-broker


# Inspect container details
docker inspect vdi-session-broker:latest

# Run container in interactive mode for debugging
docker run -it vdi-session-broker sh

# Inside container - verify non-root user
whoami
# Expected: appuser

# Inside container - check app structure
ls -la /app
# Expected:
# drwxr-xr-x    3 appuser  appuser       4096 Jan 15 10:30 .
# drwxr-xr-x    1 root     root          4096 Jan 15 10:30 ..
# drwxr-xr-x    2 appuser  appuser       4096 Jan 15 10:30 app
```

```bash
# Check running processes in container
docker run --rm vdi-session-broker ps aux

# Verify exposed ports
docker inspect vdi-session-broker:latest --format '{{.Config.ExposedPorts}}'
# Expected: map[8000/tcp:{}]

```

## Debugging & Troubleshooting

### Application Logs

```bash
# Run container with logs visible
docker run -p 8000:8000 vdi-session-broker

# Expected startup logs:
# INFO:     Started server process [1]
# INFO:     Waiting for application startup.
# INFO:     Application startup complete.
# INFO:     Uvicorn running on http://0.0.0.0:8000

# In another terminal, trigger some API calls to see request logs
curl -X POST "http://localhost:8000/sessions" \
     -H "Content-Type: application/json" \
     -d '{"userId": "debugtest"}'

```
### Common Issues & Solutions

#### Issue: Container won't start

```bash
# Check container logs
docker logs <container_id>

# Common causes:
# - Port 8000 already in use
# - Missing dependencies in requirements.txt
# - Python import errors
```

#### Issue: Tests failing

```bash
# Run tests with more verbose output
pytest tests/ -v -s --tb=long

```

#### Issue: API not responding

```bash
# Test with curl verbose mode
curl -v http://localhost:8000/health

# Check FastAPI docs are accessible
curl http://localhost:8000/docs
```


### Memory and Resource Usage

```bash
# Check container resource usage
docker stats $(docker ps -q --filter ancestor=vdi-session-broker)

# Expected output similar to:
# CONTAINER ID   NAME                CPU %   MEM USAGE / LIMIT   MEM %   NET I/O     BLOCK I/O   PIDS
# abc123def456   vdi-session-broker  0.1%    25.5MiB / 2GiB      1.27%   1.2kB/648B  0B / 0B     4

# Check memory usage inside container
docker exec -it <container_id> cat /proc/meminfo | grep MemAvailable
```

## CI/CD Pipeline

The project includes a comprehensive GitHub Actions pipeline that:

1. **Tests**: Runs pytest with coverage requirements
2. **Builds**: Creates optimized Docker container
3. **Security**: Scans for vulnerabilities with Trivy
4. **Metrics**: Collects performance and size metrics
5. **Deploy**: Prepares for deployment (placeholder)

### Triggering CI/CD
Pipeline runs on pushes to main & pull requests.

## Support

For issues or questions:
1. Check the [Debugging & Troubleshooting](#debugging--troubleshooting) section
2. Review container logs: `docker logs <container_id>`
3. Test with the interactive API docs: `http://localhost:8000/docs`
4. Verify all tests pass: `pytest tests/ -v`