# Use official slim Python 3.11 image
FROM python:3.11-slim

# Prevent Python from writing .pyc files, enable unbuffered logging, and set PYTHONPATH
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Set workspace directory
WORKDIR /app

# Install curl for healthchecks/diagnostics (no heavy C++ build-essential needed without ChromaDB)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /lib/apt/lists/*

# Copy dependency specifications first to leverage Docker layer caching
COPY requirements.txt .

# Install Python packages + ensure Phase 3/4 verification packages are present
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt \
    pytest pytest-html pydantic langgraph langchain-ollama

# Copy application source code, requirements SSOT, state manifest, and test assets
COPY src/ ./src/
COPY aspice_requirements.json ./aspice_requirements.json
COPY verification_stat[e].json ./
COPY pytest.in[i] ./
COPY tests/ ./tests/

# Create persistent directories for tests and partitioned/compliance reports
RUN mkdir -p tests reports/passed reports/failed reports/compliance

# Default execution entrypoint running the Phase 4 Agentic V&V Orchestrator
CMD ["python", "src/run_pipeline.py"]