"""Reglas de negocio del agregado Ejemplo."""
from dataclasses import dataclass

from seedwork.dominio.reglas import ReglaNegocio
from modulos.ejemplo.dominio.objetos_valor import Nombre


@dataclass
class ElNombreEsObligatorio(ReglaNegocio):
    nombre: Nombre | None = None

    def __init__(self, nombre, mensaje="El ejemplo debe tener un nombre"):
        super().__init__(mensaje)
        self.nombre = nombre

    def es_valido(self) -> bool:
        return self.nombre is not None and bool(self.nombre.valor.strip())
