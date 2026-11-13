FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
# pasang font dejavu buat cetak kartu PNG + curl buat healthcheck, sekalian bikin user sistem halio
RUN apt-get update && apt-get install -y --no-install-recommends fonts-dejavu-core curl && rm -rf /var/lib/apt/lists/* \
    && groupadd --system halio && useradd --system --gid halio --home /app halio

WORKDIR /app
# copy requirements duluan biar layer pip tetep ke-cache kl cuma ubah kode
COPY backend/requirements.txt backend/requirements-optional.txt backend/
RUN pip install --no-cache-dir -r backend/requirements.txt -r backend/requirements-optional.txt

COPY backend backend
COPY data data
COPY web web
# siapin folder /data buat nyimpen sqlite sm hak akses user non-root
RUN mkdir -p /data && chown -R halio:halio /data /app
USER halio

WORKDIR /app/backend
EXPOSE 8000
# jalanin 1 worker aja biar sqlite & penghitung kuota harian per proses ga bentrok
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 CMD curl --fail http://localhost:8000/ready || exit 1
CMD ["uvicorn", "halio.api:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
