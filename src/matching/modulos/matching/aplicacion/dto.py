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
