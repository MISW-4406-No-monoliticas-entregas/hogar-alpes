"""Registro de traductores por partner (resolución por partner_id).

Agregar un partner nuevo = agregar una clase Traductor y registrarla aquí, sin
tocar el resto del servicio (escenario 4 de modificabilidad, cualitativo).
"""
from modulos.sincronizaciones.aplicacion.traductores.base import Traductor
from modulos.sincronizaciones.aplicacion.traductores.seguros_alpes import (
    TraductorSegurosAlpes,
)
from modulos.sincronizaciones.aplicacion.traductores.banco_andes import (
    TraductorBancoAndes,
)


class PartnerDesconocido(Exception):
    """No hay traductor registrado para ese partner_id."""


class RegistroDeTraductores:
    def __init__(self):
        self._traductores: dict[str, Traductor] = {
            "seguros-alpes": TraductorSegurosAlpes(),
            "banco-andes": TraductorBancoAndes(),
        }

    def resolver(self, partner_id: str) -> Traductor:
        traductor = self._traductores.get(partner_id)
        if traductor is None:
            raise PartnerDesconocido(partner_id)
        return traductor


# Instancia única (los traductores no tienen estado).
registro_de_traductores = RegistroDeTraductores()
