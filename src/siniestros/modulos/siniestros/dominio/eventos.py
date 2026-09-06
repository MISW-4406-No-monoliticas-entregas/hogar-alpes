"""Eventos de dominio del módulo siniestros."""
import uuid
from dataclasses import dataclass, field

from seedwork.dominio.eventos import EventoDominio


@dataclass
class SiniestroRegistrado(EventoDominio):
    id_siniestro: uuid.UUID = None
    partner_id: str = None
    poliza: str = None
    monto: float = None
    moneda: str = None
    estado: str = None


@dataclass
class ProveedorAsignado(EventoDominio):
    id_siniestro: uuid.UUID = None
    proveedor_id: str = None
    estado: str = None
