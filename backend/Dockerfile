FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app \
    PORT=8000

# Runtime dependencies required by OpenCV, FFmpeg and ML workloads.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ffmpeg \
        libgl1 \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender1 \
        libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first so Docker can cache this layer.
COPY requirements.txt .

RUN python -m pip install --upgrade pip \
    && python -m pip install --no-cache-dir -r requirements.txt

# Copy only application/runtime assets.
COPY app ./app
COPY static ./static

# Create an unprivileged runtime user and application directories.
RUN useradd \
        --create-home \
        --shell /usr/sbin/nologin \
        --uid 10001 \
        appuser \
    && mkdir -p \
        /app/static/heatmaps \
        /app/static/uploads/videos \
        /app/static/uploads/captures \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]