"""Configuracion por variables de entorno. Los valores reales los inyecta el compose."""
import os


def _bd_url() -> str:
    url_completa = os.getenv("DATABASE_URL")
    if url_completa:
        return url_completa
    usuario = os.getenv("DB_USER", "reglas")
    clave = os.getenv("DB_PASSWORD", "reglas")
    host = os.getenv("DB_HOST", "localhost")
    puerto = os.getenv("DB_PORT", "5432")
    nombre = os.getenv("DB_NAME", "reglas")
    return f"postgresql+psycopg2://{usuario}:{clave}@{host}:{puerto}/{nombre}"


DATABASE_URL = _bd_url()

PULSAR_URL = os.getenv("PULSAR_URL", "pulsar://localhost:6650")

NS = "persistent://hogar-alpes/siniestros-b2b2c"

TOPICO_COMANDOS = os.getenv("TOPICO_COMANDOS", f"{NS}/comandos.reglas")
TOPICO_EVENTOS = os.getenv("TOPICO_EVENTOS", f"{NS}/eventos.reglas")
TOPICO_EVENTOS_SINIESTROS = os.getenv("TOPICO_EVENTOS_SINIESTROS", f"{NS}/eventos.siniestros")

SUSCRIPCION = os.getenv("PULSAR_SUSCRIPCION", "sub-reglas")
CONSUMIR_COMANDOS = os.getenv("CONSUMIR_COMANDOS", "true").lower() == "true"
ESCUCHAR_EVENTOS_SINIESTROS = os.getenv("ESCUCHAR_EVENTOS_SINIESTROS", "true").lower() == "true"
CARGAR_SEMILLA = os.getenv("CARGAR_SEMILLA", "true").lower() == "true"
