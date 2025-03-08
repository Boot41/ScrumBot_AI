# Stage 1: Frontend Build
FROM node:20 as frontend_build
WORKDIR /app/client
COPY client/package*.json ./
RUN npm install
COPY client/ ./
RUN npm run build

# Stage 2: Python Backend
FROM python:3.10-slim as stage-1

# Set working directory
WORKDIR /app/server

# Install system dependencies
RUN apt-get update && \
    apt-get install -y portaudio19-dev python3-pyaudio gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install additional dependencies
RUN pip install hypercorn

# Create static directory
RUN mkdir -p /app/static

# Copy frontend build from previous stage (copy the entire build directory)
COPY --from=frontend_build /app/client/build /app/static

# Copy server code
COPY server/ .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV QUART_APP=server:app
ENV QUART_ENV=production

# Command to run the application
CMD ["hypercorn", "--bind", "0.0.0.0:8000", "--access-log", "-", "server:app"]
