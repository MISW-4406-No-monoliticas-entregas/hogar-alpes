"""Configuración por variables de entorno (valores por defecto de desarrollo).

Slice de D para S4 (compensación + Saga Log): trae las variables que hacen
falta para su parte -- BD propia, y los tópicos de S10/S7 a los que se
suscribe para compensar y en los que publica las compensaciones. Quien
ensamble el servicio completo (con el camino feliz de C) añade aquí lo que
le falte, sin tocar lo de D.
"""
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

# Tópicos de otros servicios a los que D se suscribe para reaccionar a fallos.
TOPICO_EVENTOS_REGLAS = os.getenv(
    "TOPICO_EVENTOS_REGLAS", "persistent://hogar-alpes/siniestros-b2b2c/eventos.reglas"
)
TOPICO_EVENTOS_MATCHING = os.getenv(
    "TOPICO_EVENTOS_MATCHING",
    "persistent://hogar-alpes/siniestros-b2b2c/eventos.matching",
)

# Tópicos de otros servicios en los que D publica las compensaciones.
TOPICO_COMANDOS_SINIESTROS = os.getenv(
    "TOPICO_COMANDOS_SINIESTROS",
    "persistent://hogar-alpes/siniestros-b2b2c/comandos.siniestros",
)
TOPICO_COMANDOS_MATCHING = os.getenv(
    "TOPICO_COMANDOS_MATCHING",
    "persistent://hogar-alpes/siniestros-b2b2c/comandos.matching",
)

SUSCRIPCION = os.getenv("PULSAR_SUSCRIPCION", "orquestador")
