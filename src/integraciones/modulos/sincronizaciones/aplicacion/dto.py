"""DTOs de aplicación del módulo sincronizaciones."""
from dataclasses import dataclass

from seedwork.aplicacion.dto import DTO


@dataclass(frozen=True)
class SiniestroCanonico(DTO):
    """Modelo canónico interno al que cada traductor lleva el JSON del partner."""
    partner_id: str = None
    id_externo: str = None
    poliza: str = None
    monto: float = None
    moneda: str = "COP"
    calle: str = None
    ciudad: str = None
    pais: str = "CO"


@dataclass(frozen=True)
class SincronizacionDTO(DTO):
    """DTO de lectura para las queries GET."""
    id: str = None
    partner_id: str = None
    id_externo: str = None
    id_siniestro: str = None
    estado: str = None
    recibido_en: int = None
    publicado_en: int = None
