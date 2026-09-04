"""Fábrica del agregado Siniestro.

Decisión de diseño: la fábrica encapsula el ensamblado del agregado a partir de
objetos valor y dispara registrar() para que las invariantes se apliquen en la
construcción. Así el handler del comando no arma el agregado a mano ni conoce
las reglas: solo pide "créame un siniestro válido".
"""
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
        """No se usa: la fábrica recibe objetos valor ya armados."""
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
