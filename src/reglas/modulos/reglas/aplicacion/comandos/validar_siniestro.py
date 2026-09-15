"""Comando ValidarSiniestro y su handler.

El mismo handler sirve para las dos entradas. Cuando el comando llega por el
topico trae `id_mensaje` y se registra dentro de la misma Unidad de Trabajo que
el trabajo de negocio, de modo que una reentrega no produce dos validaciones.
"""
from dataclasses import dataclass

from seedwork.aplicacion.comandos import Comando, ComandoHandler, ejecutar_comando
from seedwork.infraestructura.idempotencia import registrar_mensaje, MensajeDuplicado
from modulos.reglas.dominio.fabricas import FabricaValidacion
from modulos.reglas.dominio.objetos_valor import Monto, PartnerId, Servicio, Zona
from modulos.reglas.aplicacion.servicios import (
    nueva_uow,
    repositorio_reglas_en,
    repositorio_validaciones_en,
)


@dataclass
class ValidarSiniestro(Comando):
    id_siniestro: str
    partner_id: str
    monto: float
    moneda: str = "COP"
    servicio: str = ""
    zona: str = ""
    id_mensaje: str | None = None


class ValidarSiniestroHandler(ComandoHandler):
    def __init__(self):
        self.fabrica = FabricaValidacion()

    def handle(self, comando: ValidarSiniestro) -> str | None:
        partner_id = PartnerId(comando.partner_id)
        monto = Monto(comando.monto, comando.moneda)
        servicio = Servicio(comando.servicio)
        zona = Zona(comando.zona)

        with nueva_uow() as uow:
            if comando.id_mensaje:
                try:
                    registrar_mensaje(uow.session, comando.id_mensaje)
                except MensajeDuplicado:
                    return None

            regla = repositorio_reglas_en(uow).obtener_por_partner(comando.partner_id)
            if regla is None:
                validacion = self.fabrica.crear_validacion_sin_regla(
                    partner_id, comando.id_siniestro, monto, servicio, zona
                )
            else:
                validacion = self.fabrica.crear_validacion(
                    regla, comando.id_siniestro, monto, servicio, zona
                )

            repositorio_validaciones_en(uow).agregar(validacion)
            uow.registrar_agregado(validacion)
            uow.commit()
        return str(validacion.id)


@ejecutar_comando.register(ValidarSiniestro)
def _(comando: ValidarSiniestro):
    return ValidarSiniestroHandler().handle(comando)
