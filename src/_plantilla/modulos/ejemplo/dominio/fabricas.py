"""Fábrica del agregado Ejemplo.

La fábrica encapsula el ensamblado del agregado y dispara sus invariantes, de
modo que un Ejemplo nunca exista en estado inválido.
"""
from dataclasses import dataclass

from seedwork.dominio.fabricas import Fabrica
from modulos.ejemplo.dominio.entidades import Ejemplo
from modulos.ejemplo.dominio.objetos_valor import Nombre


@dataclass
class FabricaEjemplo(Fabrica):
    def crear_objeto(self, obj, mapeador=None):
        raise NotImplementedError

    def crear_ejemplo(self, nombre: Nombre) -> Ejemplo:
        ejemplo = Ejemplo(nombre=nombre)
        ejemplo.crear()
        return ejemplo
