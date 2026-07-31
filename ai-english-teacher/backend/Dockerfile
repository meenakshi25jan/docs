FROM python:3.12-slim AS base

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY backend/requirements-render.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .
COPY database/migrations /app/migrations

RUN chmod +x start.sh

ENV SKIP_MIGRATIONS=false
ENV PYTHONPATH=/app
EXPOSE 8000

CMD ["./start.sh"]
