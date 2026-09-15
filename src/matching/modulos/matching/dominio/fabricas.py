"""Fábrica del agregado Asignacion.

Decide, a partir de si hay o no un proveedor disponible, si la asignación
queda ASIGNADA o SIN_PROVEEDOR, y dispara las invariantes al ensamblarla.
"""
from dataclasses import dataclass

from seedwork.dominio.fabricas import Fabrica
from modulos.matching.dominio.entidades import Asignacion, ProveedorHabilitado
from modulos.matching.dominio.objetos_valor import Servicio, Zona


@dataclass
class FabricaAsignacion(Fabrica):
    def crear_objeto(self, obj, mapeador=None):
        raise NotImplementedError

    def crear_asignacion(
        self,
        id_siniestro: str,
        servicio: Servicio,
        zona: Zona,
        proveedor: ProveedorHabilitado | None,
    ) -> Asignacion:
        asignacion = Asignacion(id_siniestro=id_siniestro, servicio=servicio, zona=zona)
        if proveedor is not None:
            asignacion.asignar(proveedor)
        else:
            asignacion.marcar_sin_proveedor()
        return asignacion
