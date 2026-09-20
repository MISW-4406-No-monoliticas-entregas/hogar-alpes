"""DTOs de aplicación del módulo orquestador (lado de lectura)."""
from dataclasses import dataclass

from seedwork.aplicacion.dto import DTO


@dataclass(frozen=True)
class SagaDTO(DTO):
    id: str = None
    siniestro_id: str = None
    paso_actual: str = None
    estado: str = None
    proveedor_id: str = None
    motivo_fallo: str = None
