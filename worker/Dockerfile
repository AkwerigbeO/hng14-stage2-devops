# Stage 1: Build dependencies
FROM python:3.11-slim AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip wheel --no-cache-dir --wheel-dir /app/wheels -r requirements.txt

# Stage 2: Final production image
FROM python:3.11-slim

WORKDIR /app

# Create a non-root user
RUN adduser --disabled-password --no-create-home appuser

# Install procps for pgrep (used in healthcheck)
RUN apt-get update && \
    apt-get install -y --no-install-recommends procps && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache-dir /wheels/*

COPY worker.py .

RUN chown -R appuser:appuser /app

USER appuser

# Environment variables
ENV REDIS_HOST=localhost
ENV REDIS_PORT=6379

# Healthcheck to verify the worker process is running
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD pgrep -f worker.py || exit 1

CMD ["python", "worker.py"]
