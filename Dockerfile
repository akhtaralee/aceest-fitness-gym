# ─────────────────────────────────────────────
# ACEest Fitness & Gym – Docker Image
# Multi-stage build: slim Python 3.12
# ─────────────────────────────────────────────

FROM python:3.12-slim AS base

# Prevent Python from writing .pyc files & enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY app.py .
COPY test_app.py .

# Expose the Flask port
EXPOSE 5000

# Health check so orchestrators can verify the container
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

# Run with Gunicorn in production
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]
