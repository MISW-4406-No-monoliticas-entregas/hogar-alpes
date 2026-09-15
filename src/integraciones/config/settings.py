"""Configuración por variables de entorno (valores por defecto de desarrollo)."""
import os


def _bd_url() -> str:
    url_completa = os.getenv("DATABASE_URL")
    if url_completa:
        return url_completa
    usuario = os.getenv("DB_USER", "integraciones")
    clave = os.getenv("DB_PASSWORD", "integraciones")
    host = os.getenv("DB_HOST", "localhost")
    puerto = os.getenv("DB_PORT", "5432")
    nombre = os.getenv("DB_NAME", "integraciones")
    return f"postgresql+psycopg2://{usuario}:{clave}@{host}:{puerto}/{nombre}"


DATABASE_URL = _bd_url()

PULSAR_URL = os.getenv("PULSAR_URL", "pulsar://localhost:6650")

# Salidas de S9 (nombres completos del namespace, inyectados por el compose):
#  - el COMANDO canónico que consume Siniestros (S2)
TOPICO_COMANDOS_SINIESTROS = os.getenv(
    "TOPICO_COMANDOS_SINIESTROS",
    "persistent://hogar-alpes/siniestros-b2b2c/comandos.siniestros",
)
#  - el EVENTO de integración propio de S9
TOPICO_EVENTOS = os.getenv(
    "TOPICO_EVENTOS", "persistent://hogar-alpes/siniestros-b2b2c/eventos.partners"
)
