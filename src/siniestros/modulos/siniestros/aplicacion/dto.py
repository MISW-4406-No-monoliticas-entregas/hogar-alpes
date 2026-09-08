"""DTOs de aplicación del módulo siniestros."""
from dataclasses import dataclass, field

from seedwork.aplicacion.dto import DTO


@dataclass(frozen=True)
class SiniestroDTO(DTO):
    partner_id: str = None
    poliza: str = None
    monto: float = None
    moneda: str = "COP"
    calle: str = None
    ciudad: str = None
    pais: str = "CO"
    id: str = None
    estado: str = None
    proveedor_id: str = None
