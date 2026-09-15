"""Eventos de dominio del módulo matching."""
import uuid
from dataclasses import dataclass

from seedwork.dominio.eventos import EventoDominio


@dataclass
class ProveedorAsignado(EventoDominio):
    id_asignacion: uuid.UUID = None
    id_siniestro: str = None
    proveedor_id: str = None
    nombre_proveedor: str = None
    servicio: str = None
    zona: str = None
    estado: str = None


@dataclass
class SinProveedorDisponible(EventoDominio):
    id_asignacion: uuid.UUID = None
    id_siniestro: str = None
    servicio: str = None
    zona: str = None
    estado: str = None
