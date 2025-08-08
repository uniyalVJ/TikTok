# Install requirements
pip install -r requirements.txt


# Run Tests in session-broker/
pytest tests/ -v


# Dockerfile Test
docker build -t vdi-session-broker .

# Run container and map port 8000
docker run -p 8000:8000 vdi-session-broker


# Test the API Endpoints

# Create Session - Returns SessionId
curl -X POST "http://localhost:8000/sessions" \
     -H "Content-Type: application/json" \
     -d '{"userId": "dockertest"}'


# Get Session - Use SessionId from above response
curl -X GET "http://localhost:8000/sessions/YOUR_SESSION_ID_HERE"


# Terminate Session
curl -X DELETE "http://localhost:8000/sessions/YOUR_SESSION_ID_HERE"

# Interactive API Test, with container running open browser to:
http://localhost:8000/docs

# Check Image Size
docker images vdi-session-broker

# Run the Container in Interactive mode to Inspect
docker run -it --entrypoint /bin/sh vdi-session-broker

# Confirm non-root user "appuser"
whoami

# Show your app files
ls -la /app 

#
