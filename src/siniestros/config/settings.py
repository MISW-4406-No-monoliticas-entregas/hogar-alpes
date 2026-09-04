"""Configuración por variables de entorno (valores de desarrollo por defecto).

Ítem "repositorio público sin credenciales": todo sale de variables de entorno;
los defaults son de desarrollo y coinciden con los del docker-compose.
"""
import os


def _bd_url() -> str:
    """Devuelve la URL de la base de datos.

    Si existe la variable DATABASE_URL se usa completa (plataformas que la
    exponen directamente, o pruebas con un motor sin driver Postgres). Si no,
    se arma la URL de PostgreSQL desde sus partes (caso Docker).
    """
    url_completa = os.getenv("DATABASE_URL")
    if url_completa:
        return url_completa
    usuario = os.getenv("DB_USER", "siniestros")
    clave = os.getenv("DB_PASSWORD", "siniestros")
    host = os.getenv("DB_HOST", "localhost")
    puerto = os.getenv("DB_PORT", "5432")
    nombre = os.getenv("DB_NAME", "siniestros")
    return f"postgresql+psycopg2://{usuario}:{clave}@{host}:{puerto}/{nombre}"


DATABASE_URL = _bd_url()

PULSAR_URL = os.getenv("PULSAR_URL", "pulsar://localhost:6650")
TOPICO_EVENTOS = os.getenv("TOPICO_EVENTOS", "eventos.trabajos")
TOPICO_COMANDOS = os.getenv("TOPICO_COMANDOS", "comandos.siniestros")
SUSCRIPCION = os.getenv("PULSAR_SUSCRIPCION", "trabajos-siniestros")
