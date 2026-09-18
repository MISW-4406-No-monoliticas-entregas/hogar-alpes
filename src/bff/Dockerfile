# El BFF es autocontenido: su contexto de build es su propia carpeta.
# No necesita libpq ni gcc: no tiene base de datos ni cliente de Pulsar.
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app

EXPOSE 5000

CMD ["python", "main.py"]
