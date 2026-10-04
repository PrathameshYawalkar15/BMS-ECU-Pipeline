# Use official slim Python 3.11 image
FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set workspace directory
WORKDIR /app

# Install system dependencies required for compilation/C++ tools (e.g., ChromaDB dependencies)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /lib/apt/lists/*

# Copy dependency specifications first to leverage Docker layer caching
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code and assets into the container
COPY src/ ./src/
COPY .env .env

# Create persistent mount points for chroma_db, tests, and reports
RUN mkdir -p chroma_db tests reports

# Copy chroma_db directory if it exists on host (non-blocking wildcards)
COPY chroma_d[b] ./chroma_db/

# Default execution entrypoint running the LangGraph agent graph
CMD ["python", "src/agent_graph.py"]