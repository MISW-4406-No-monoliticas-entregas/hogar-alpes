# Cada servicio es autocontenido: su contexto de build es su propia carpeta.
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# El contexto de build es src/siniestros, así que copiamos todo el servicio.
COPY . .

ENV PYTHONPATH=/app

EXPOSE 5000

CMD ["python", "main.py"]
