"""Fábrica del agregado Siniestro."""
from dataclasses import dataclass

from seedwork.dominio.fabricas import Fabrica
from modulos.siniestros.dominio.entidades import Siniestro
from modulos.siniestros.dominio.objetos_valor import (
    PartnerId,
    Poliza,
    Monto,
    Direccion,
)


@dataclass
class FabricaSiniestro(Fabrica):
    def crear_objeto(self, obj, mapeador=None):
        raise NotImplementedError

    def crear_siniestro(
        self,
        partner_id: PartnerId,
        poliza: Poliza,
        monto: Monto,
        direccion: Direccion,
    ) -> Siniestro:
        siniestro = Siniestro(
            partner_id=partner_id,
            poliza=poliza,
            monto=monto,
            direccion=direccion,
        )
        siniestro.registrar()
        return siniestro
