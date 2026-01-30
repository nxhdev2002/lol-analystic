# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY language/ ./language/

# Create necessary directories
RUN mkdir -p logs

# Set default environment variables (can be overridden at runtime)
ENV RIOT_API_KEY="" \
    GEMINI_API_KEY="" \
    OPENAI_API_KEY="" \
    AI_PROVIDER="gemini" \
    OPENAI_BASE_URL="https://api.openai.com/v1" \
    OPENAI_MODEL="gpt-4o-mini"

# Expose port if needed (for health checks or webhooks)
# EXPOSE 8080

# Run the application
CMD ["python", "src/main.py"]
