"""Configuración por variables de entorno (valores por defecto de desarrollo).

Al crear tu servicio, cambia los defaults y los nombres de tópico en el
docker-compose, no aquí: aquí solo se leen del entorno.
"""
import os


def _bd_url() -> str:
    url_completa = os.getenv("DATABASE_URL")
    if url_completa:
        return url_completa
    usuario = os.getenv("DB_USER", "matching")
    clave = os.getenv("DB_PASSWORD", "matching")
    host = os.getenv("DB_HOST", "localhost")
    puerto = os.getenv("DB_PORT", "5432")
    nombre = os.getenv("DB_NAME", "matching")
    return f"postgresql+psycopg2://{usuario}:{clave}@{host}:{puerto}/{nombre}"


DATABASE_URL = _bd_url()

PULSAR_URL = os.getenv("PULSAR_URL", "pulsar://localhost:6650")

# Nombres completos del namespace, inyectados por el docker-compose.
TOPICO_COMANDOS = os.getenv(
    "TOPICO_COMANDOS", "persistent://hogar-alpes/siniestros-b2b2c/comandos.matching"
)
TOPICO_EVENTOS = os.getenv(
    "TOPICO_EVENTOS", "persistent://hogar-alpes/siniestros-b2b2c/eventos.matching"
)
# Tópico de otro servicio (S2) al que S7 solo se suscribe para registrar en log.
TOPICO_EVENTOS_SINIESTROS = os.getenv(
    "TOPICO_EVENTOS_SINIESTROS",
    "persistent://hogar-alpes/siniestros-b2b2c/eventos.siniestros",
)

SUSCRIPCION = os.getenv("PULSAR_SUSCRIPCION", "matching")
CONSUMIR_COMANDOS = os.getenv("CONSUMIR_COMANDOS", "true").lower() == "true"
CONSUMIR_EVENTOS_SINIESTROS = (
    os.getenv("CONSUMIR_EVENTOS_SINIESTROS", "true").lower() == "true"
)
