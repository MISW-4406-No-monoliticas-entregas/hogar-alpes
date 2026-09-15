"""Eventos de dominio del modulo reglas."""
import uuid
from dataclasses import dataclass

from seedwork.dominio.eventos import EventoDominio


@dataclass
class SiniestroAprobadoPorReglas(EventoDominio):
    id_validacion: uuid.UUID = None
    id_siniestro: str = None
    partner_id: str = None
    monto: float = None
    moneda: str = None
    servicio: str = None
    zona: str = None
    motivo: str = None


@dataclass
class SiniestroRechazadoPorReglas(EventoDominio):
    id_validacion: uuid.UUID = None
    id_siniestro: str = None
    partner_id: str = None
    monto: float = None
    moneda: str = None
    servicio: str = None
    zona: str = None
    motivo: str = None
