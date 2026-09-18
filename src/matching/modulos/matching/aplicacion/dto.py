"""DTOs de aplicación del módulo matching (lado de lectura)."""
from dataclasses import dataclass

from seedwork.aplicacion.dto import DTO


@dataclass(frozen=True)
class ProveedorHabilitadoDTO(DTO):
    id: str = None
    nombre: str = None
    servicio: str = None
    zona: str = None
    disponible: bool = None


@dataclass(frozen=True)
class AsignacionDTO(DTO):
    id: str = None
    id_siniestro: str = None
    servicio: str = None
    zona: str = None
    proveedor_id: str = None
    nombre_proveedor: str = None
    estado: str = None
