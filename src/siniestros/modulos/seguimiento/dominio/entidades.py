"""Modelo de lectura (proyección) del módulo seguimiento."""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class EstadoDeSiniestro:
    id_siniestro: str
    partner_id: str
    estado: str
    poliza: str | None = None
    monto: float | None = None
    moneda: str | None = None
    proveedor_id: str | None = None
    fecha_actualizacion: datetime | None = None
