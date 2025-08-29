FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# WeasyPrint OS deps + curl for debugging/health
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 libpangocairo-1.0-0 libcairo2 libgdk-pixbuf2.0-0 \
    libffi8 libjpeg62-turbo libpng16-16 \
    fonts-dejavu fonts-noto-core \
    curl \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Keep memory use low on the free plan
ENV WEB_CONCURRENCY=1

# Render provides $PORT; default to 10000 if run locally
EXPOSE 10000

CMD exec gunicorn \
  -k uvicorn.workers.UvicornWorker \
  -w ${WEB_CONCURRENCY} \
  -b 0.0.0.0:${PORT:-10000} \
  app:app \
  --timeout 120 --graceful-timeout 30 --keep-alive 5 --access-logfile -
