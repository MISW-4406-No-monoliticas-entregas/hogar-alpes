"""Fábrica del agregado Sincronizacion."""
from dataclasses import dataclass

from seedwork.dominio.fabricas import Fabrica
from modulos.sincronizaciones.dominio.entidades import Sincronizacion
from modulos.sincronizaciones.dominio.objetos_valor import (
    PartnerId,
    IdExterno,
    EstadoSincronizacion,
)


@dataclass
class FabricaSincronizacion(Fabrica):
    def crear_objeto(self, obj, mapeador=None):
        raise NotImplementedError

    def crear_sincronizacion(self, partner_id: str, id_externo: str) -> Sincronizacion:
        return Sincronizacion(
            partner_id=PartnerId(partner_id),
            id_externo=IdExterno(id_externo),
            estado=EstadoSincronizacion.RECIBIDA,
        )
