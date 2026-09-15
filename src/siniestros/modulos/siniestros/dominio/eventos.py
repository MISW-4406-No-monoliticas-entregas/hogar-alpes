"""Eventos de dominio del módulo siniestros.

Con event sourcing el flujo de eventos es la ÚNICA fuente de verdad, así que
SiniestroRegistrado lleva también la dirección: si no viajara en el evento, el
dato se perdería al reconstruir el agregado desde el event store.
"""
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
    calle: str = ""
    ciudad: str = ""
    pais: str = "CO"


@dataclass
class ProveedorAsignado(EventoDominio):
    id_siniestro: uuid.UUID = None
    proveedor_id: str = None
    estado: str = None


@dataclass
class SiniestroValidado(EventoDominio):
    id_siniestro: uuid.UUID = None
    estado: str = None


@dataclass
class SiniestroRechazado(EventoDominio):
    id_siniestro: uuid.UUID = None
    motivo: str = None
    estado: str = None
