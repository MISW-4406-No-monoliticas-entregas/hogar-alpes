"""Entidades del módulo ejemplo: agregado Ejemplo."""
from dataclasses import dataclass

from seedwork.dominio.entidades import AgregacionRaiz
from modulos.ejemplo.dominio.objetos_valor import Nombre, EstadoEjemplo
from modulos.ejemplo.dominio.eventos import EjemploCreado
from modulos.ejemplo.dominio.reglas import ElNombreEsObligatorio


@dataclass
class Ejemplo(AgregacionRaiz):
    """Agregado raíz de ejemplo (reemplázalo por el tuyo)."""
    nombre: Nombre = None
    estado: EstadoEjemplo = None

    def crear(self):
        """Valida las invariantes y emite el evento de dominio."""
        self.validar_regla(ElNombreEsObligatorio(self.nombre))
        self.estado = EstadoEjemplo.CREADO
        self.agregar_evento(
            EjemploCreado(
                id_ejemplo=self.id,
                nombre=self.nombre.valor,
                estado=self.estado.value,
            )
        )
