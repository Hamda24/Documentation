FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# WeasyPrint OS deps + curl for health/debug
RUN apt-get update && apt-get install -y --no-install-recommends \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi8 \
    libjpeg62-turbo \
    libpng16-16 \
    shared-mime-info \
    fonts-dejavu \
    fonts-noto-core \
    curl \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Keep memory low on free plan
ENV WEB_CONCURRENCY=1
EXPOSE 10000

CMD exec gunicorn \
  -k uvicorn.workers.UvicornWorker \
  -w ${WEB_CONCURRENCY} \
  -b 0.0.0.0:${PORT:-10000} \
  app:app \
  --timeout 120 --graceful-timeout 30 --keep-alive 5 --access-logfile -
