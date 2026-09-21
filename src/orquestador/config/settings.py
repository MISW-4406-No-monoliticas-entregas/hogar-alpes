"""Configuracion por variables de entorno (valores por defecto de desarrollo)."""
import os


def _bd_url() -> str:
    url_completa = os.getenv("DATABASE_URL")
    if url_completa:
        return url_completa
    usuario = os.getenv("DB_USER", "orquestador")
    clave = os.getenv("DB_PASSWORD", "orquestador")
    host = os.getenv("DB_HOST", "localhost")
    puerto = os.getenv("DB_PORT", "5432")
    nombre = os.getenv("DB_NAME", "orquestador")
    return f"postgresql+psycopg2://{usuario}:{clave}@{host}:{puerto}/{nombre}"


DATABASE_URL = _bd_url()

PULSAR_URL = os.getenv("PULSAR_URL", "pulsar://localhost:6650")

NS = "persistent://hogar-alpes/siniestros-b2b2c"

# Topicos de otros servicios a los que el orquestador se suscribe.
TOPICO_EVENTOS_SINIESTROS = os.getenv(
    "TOPICO_EVENTOS_SINIESTROS", f"{NS}/eventos.siniestros"
)
TOPICO_EVENTOS_REGLAS = os.getenv("TOPICO_EVENTOS_REGLAS", f"{NS}/eventos.reglas")
TOPICO_EVENTOS_MATCHING = os.getenv("TOPICO_EVENTOS_MATCHING", f"{NS}/eventos.matching")

# Topicos de otros servicios en los que el orquestador publica comandos.
TOPICO_COMANDOS_SINIESTROS = os.getenv(
    "TOPICO_COMANDOS_SINIESTROS", f"{NS}/comandos.siniestros"
)
TOPICO_COMANDOS_REGLAS = os.getenv("TOPICO_COMANDOS_REGLAS", f"{NS}/comandos.reglas")
TOPICO_COMANDOS_MATCHING = os.getenv(
    "TOPICO_COMANDOS_MATCHING", f"{NS}/comandos.matching"
)

SUSCRIPCION = os.getenv("PULSAR_SUSCRIPCION", "orquestador")

CONSUMIR_EVENTOS_SINIESTROS = os.getenv("CONSUMIR_EVENTOS_SINIESTROS", "true").lower() == "true"
CONSUMIR_EVENTOS_REGLAS = os.getenv("CONSUMIR_EVENTOS_REGLAS", "true").lower() == "true"
CONSUMIR_EVENTOS_MATCHING = os.getenv("CONSUMIR_EVENTOS_MATCHING", "true").lower() == "true"
