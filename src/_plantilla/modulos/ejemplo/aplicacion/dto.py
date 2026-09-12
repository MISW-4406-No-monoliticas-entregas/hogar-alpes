"""DTOs de aplicación del módulo ejemplo."""
from dataclasses import dataclass

from seedwork.aplicacion.dto import DTO


@dataclass(frozen=True)
class EjemploDTO(DTO):
    id: str = None
    nombre: str = None
    estado: str = None
