"""Excepciones del dominio."""
from seedwork.dominio.reglas import ReglaNegocio


class ExcepcionDominio(Exception):
    """Excepción base de la capa de dominio."""
    ...


class ReglaNegocioExcepcion(ExcepcionDominio):
    """Se lanza cuando se viola una regla de negocio del agregado."""

    def __init__(self, regla: ReglaNegocio):
        self.regla = regla
        super().__init__(str(regla))
