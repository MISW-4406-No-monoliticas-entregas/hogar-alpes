"""DTOs de aplicacion del modulo reglas (lado de lectura)."""
from dataclasses import dataclass, field

from seedwork.aplicacion.dto import DTO


@dataclass(frozen=True)
class ReglaDePartnerDTO(DTO):
    partner_id: str = None
    monto_maximo: float = None
    moneda: str = None
    servicios_cubiertos: list = field(default_factory=list)
    zonas_habilitadas: list = field(default_factory=list)
    activa: bool = True


@dataclass(frozen=True)
class ValidacionDTO(DTO):
    id: str = None
    id_siniestro: str = None
    partner_id: str = None
    monto: float = None
    moneda: str = None
    servicio: str = None
    zona: str = None
    resultado: str = None
    motivo: str = None
    fecha: str = None
