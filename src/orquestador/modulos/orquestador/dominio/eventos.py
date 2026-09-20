"""Eventos de dominio del módulo orquestador."""
import uuid
from dataclasses import dataclass

from seedwork.dominio.eventos import EventoDominio


@dataclass
class CompensacionIniciada(EventoDominio):
    """La saga entró en COMPENSANDO: hay que publicar las compensaciones que
    correspondan. `proveedor_id` viaja solo si la saga alcanzó a reservar uno
    antes del fallo (si no, no hay nada que liberar)."""
    id_saga: uuid.UUID = None
    siniestro_id: str = None
    motivo: str = None
    proveedor_id: str | None = None
