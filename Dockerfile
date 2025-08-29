# Use Debian 12 (bookworm) slim image with Python 3.11
FROM python:3.11-slim

# ---- System libraries WeasyPrint needs + some fonts ----
# Keep it small with --no-install-recommends
RUN apt-get update && apt-get install -y --no-install-recommends \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi8 \
    libjpeg62-turbo \
    libpng16-16 \
    fonts-dejavu \
    fonts-noto-core \
  && rm -rf /var/lib/apt/lists/*

# Where our code will live inside the container
WORKDIR /app

# Install Python deps first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project (app.py, templates/, etc.)
COPY . .

# Render sets $PORT at runtime; default to 8080 for local runs
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Expose for local docker run (Render maps ports internally)
EXPOSE 8080

# Start the API: gunicorn + uvicorn workers
CMD exec gunicorn app:app \
    -k uvicorn.workers.UvicornWorker \
    -w 2 \
    -b 0.0.0.0:${PORT}
