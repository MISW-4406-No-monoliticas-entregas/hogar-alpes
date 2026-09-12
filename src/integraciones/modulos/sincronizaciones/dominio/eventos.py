"""Eventos de dominio del módulo sincronizaciones."""
import uuid
from dataclasses import dataclass

from seedwork.dominio.eventos import EventoDominio


@dataclass
class SiniestroSincronizado(EventoDominio):
    """El siniestro del partner se tradujo y se aceptó para publicar al dominio.

    Lleva la carga canónica para que los handlers construyan el comando
    RegistrarSiniestro y el evento de integración sin volver a consultar nada.
    """
    id_sincronizacion: uuid.UUID = None
    partner_id: str = None
    id_externo: str = None
    # Carga canónica (para el comando RegistrarSiniestro):
    poliza: str = None
    monto: float = None
    moneda: str = None
    calle: str = None
    ciudad: str = None
    pais: str = None
