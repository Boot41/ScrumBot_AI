# Stage 1: Frontend Build
FROM node:20 as frontend_build
WORKDIR /app/client
COPY client/package*.json ./
RUN npm install
COPY client/ ./
RUN npm run build

# Stage 2: Python Backend
FROM python:3.10-slim

# Set working directory
WORKDIR /app/server

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    portaudio19-dev \
    python3-pyaudio \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install whitenoise gunicorn

# Create directory for static files
RUN mkdir -p /app/static

# Copy frontend build from previous stage
COPY --from=frontend_build /app/client/build/ /app/static/

# Copy server code
COPY server/ .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV STATIC_ROOT=/app/static
ENV STATIC_URL=/static/
ENV PYTHONPATH=/app/server

# Expose port
EXPOSE 8000

# Use gunicorn to serve the application
CMD ["gunicorn", "--workers", "3", "--bind", "0.0.0.0:8000", "server:app"]
