"""Configuración por variables de entorno."""
import os


def _bd_url() -> str:
    """URL de la base: DATABASE_URL si existe, si no se arma desde sus partes."""
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
PULSAR_ADMIN_URL = os.getenv("PULSAR_ADMIN_URL", "http://localhost:8080")
TOPICO_EVENTOS = os.getenv("TOPICO_EVENTOS", "eventos.trabajos")
TOPICO_COMANDOS = os.getenv("TOPICO_COMANDOS", "comandos.siniestros")
SUSCRIPCION = os.getenv("PULSAR_SUSCRIPCION", "trabajos-siniestros")
