"""Modelo de lectura del módulo seguimiento.

EstadoDeSiniestro es una proyección: una vista desnormalizada optimizada para
consulta (CQRS). No tiene reglas de negocio; se construye a partir de los
eventos de dominio que emite el módulo siniestros.
"""
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
