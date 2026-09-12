"""Configuración por variables de entorno (valores por defecto de desarrollo).

Al crear tu servicio, cambia los defaults y los nombres de tópico en el
docker-compose, no aquí: aquí solo se leen del entorno.
"""
import os


def _bd_url() -> str:
    url_completa = os.getenv("DATABASE_URL")
    if url_completa:
        return url_completa
    usuario = os.getenv("DB_USER", "plantilla")
    clave = os.getenv("DB_PASSWORD", "plantilla")
    host = os.getenv("DB_HOST", "localhost")
    puerto = os.getenv("DB_PORT", "5432")
    nombre = os.getenv("DB_NAME", "plantilla")
    return f"postgresql+psycopg2://{usuario}:{clave}@{host}:{puerto}/{nombre}"


DATABASE_URL = _bd_url()

PULSAR_URL = os.getenv("PULSAR_URL", "pulsar://localhost:6650")

# Nombres completos del namespace nuevo, inyectados por el docker-compose.
TOPICO_COMANDOS = os.getenv(
    "TOPICO_COMANDOS", "persistent://hogar-alpes/siniestros-b2b2c/comandos.ejemplo"
)
TOPICO_EVENTOS = os.getenv(
    "TOPICO_EVENTOS", "persistent://hogar-alpes/siniestros-b2b2c/eventos.ejemplo"
)
SUSCRIPCION = os.getenv("PULSAR_SUSCRIPCION", "plantilla")
CONSUMIR_COMANDOS = os.getenv("CONSUMIR_COMANDOS", "true").lower() == "true"
