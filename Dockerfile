FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y --no-install-recommends fonts-dejavu-core && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY backend/requirements.txt backend/requirements-optional.txt backend/
RUN pip install --no-cache-dir -r backend/requirements.txt gTTS anthropic

COPY backend backend
COPY data data
COPY web web

WORKDIR /app/backend
EXPOSE 8000
CMD ["uvicorn", "halio.api:app", "--host", "0.0.0.0", "--port", "8000"]
