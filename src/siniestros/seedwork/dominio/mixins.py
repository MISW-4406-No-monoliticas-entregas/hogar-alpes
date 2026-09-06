"""Mixins de dominio."""
from seedwork.dominio.reglas import ReglaNegocio
from seedwork.dominio.excepciones import ReglaNegocioExcepcion


class ValidarReglasMixin:
    """Valida reglas de negocio en entidades y agregados."""

    def validar_regla(self, regla: ReglaNegocio):
        if not regla.es_valido():
            raise ReglaNegocioExcepcion(regla)
