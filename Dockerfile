# Multi-stage Docker build for Zynx AGI Platform
FROM python:3.12-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt setup.py ./
COPY zynx_agi/ ./zynx_agi/

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Development stage
FROM base as development
ENV ZYNX_ENV=development
EXPOSE 8000
CMD ["python", "-m", "zynx_agi.main"]

# Production stage
FROM base as production
ENV ZYNX_ENV=production

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash zynx && \
    chown -R zynx:zynx /app
USER zynx

EXPOSE 8000
CMD ["python", "-m", "zynx_agi.monitoring.zynx_main_with_monitoring"]