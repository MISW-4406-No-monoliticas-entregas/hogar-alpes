"""Objetos valor del módulo sincronizaciones."""
from dataclasses import dataclass
from enum import Enum

from seedwork.dominio.objetos_valor import ObjetoValor


class EstadoSincronizacion(str, Enum):
    RECIBIDA = "RECIBIDA"      # se recibió del partner y se tradujo
    PUBLICADA = "PUBLICADA"    # se publicó el comando canónico al dominio
    DUPLICADA = "DUPLICADA"    # ya existía (partner_id + id_externo)
    RECHAZADA = "RECHAZADA"    # partner desconocido o payload inválido


@dataclass(frozen=True)
class PartnerId(ObjetoValor):
    valor: str


@dataclass(frozen=True)
class IdExterno(ObjetoValor):
    """Identificador del siniestro en el sistema del partner (su referencia)."""
    valor: str
