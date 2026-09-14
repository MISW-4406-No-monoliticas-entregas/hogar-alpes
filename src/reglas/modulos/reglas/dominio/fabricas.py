"""Fabricas de los agregados del modulo reglas.

Encapsulan el ensamblado y disparan las invariantes, de modo que ni una regla de
partner ni una validacion puedan existir en estado invalido.
"""
from dataclasses import dataclass

from seedwork.dominio.fabricas import Fabrica
from modulos.reglas.dominio.entidades import ReglaDePartner, Validacion
from modulos.reglas.dominio.objetos_valor import (
    Evaluacion,
    Monto,
    PartnerId,
    ResultadoValidacion,
    Servicio,
    Zona,
)


@dataclass
class FabricaReglaDePartner(Fabrica):
    def crear_objeto(self, obj, mapeador=None):
        raise NotImplementedError

    def crear_regla(
        self,
        partner_id: PartnerId,
        monto_maximo: Monto,
        servicios_cubiertos: list[Servicio],
        zonas_habilitadas: list[Zona],
    ) -> ReglaDePartner:
        regla = ReglaDePartner(
            partner_id=partner_id,
            monto_maximo=monto_maximo,
            servicios_cubiertos=servicios_cubiertos,
            zonas_habilitadas=zonas_habilitadas,
        )
        regla.definir()
        return regla


@dataclass
class FabricaValidacion(Fabrica):
    def crear_objeto(self, obj, mapeador=None):
        raise NotImplementedError

    def crear_validacion(
        self,
        regla: ReglaDePartner,
        id_siniestro: str,
        monto: Monto,
        servicio: Servicio,
        zona: Zona,
    ) -> Validacion:
        validacion = Validacion(
            id_siniestro=id_siniestro,
            partner_id=regla.partner_id,
            monto=monto,
            servicio=servicio,
            zona=zona,
        )
        validacion.registrar(regla.evaluar(monto, servicio, zona))
        return validacion

    def crear_validacion_sin_regla(
        self,
        partner_id: PartnerId,
        id_siniestro: str,
        monto: Monto,
        servicio: Servicio,
        zona: Zona,
    ) -> Validacion:
        """El partner no tiene contrato cargado: se rechaza y queda registrado."""
        validacion = Validacion(
            id_siniestro=id_siniestro,
            partner_id=partner_id,
            monto=monto,
            servicio=servicio,
            zona=zona,
        )
        validacion.registrar(
            Evaluacion(
                ResultadoValidacion.RECHAZADO,
                "No hay reglas configuradas para el partner",
            )
        )
        return validacion
