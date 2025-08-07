# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

COPY requirements.txt .

# Install requirements, --user flag installs packages in the user's home directory
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage  
FROM python:3.11-slim

# Create Non-Root User
# This is a security best practice to avoid running applications as root
RUN useradd -m -u 1000 appuser 

WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /root/.local /home/appuser/.local

# Copy Application
COPY app/ ./app/

RUN chown -R appuser:appuser /app

USER appuser

# Update PATH
ENV PATH="/home/appuser/.local/bin:$PATH"

EXPOSE 8080

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]