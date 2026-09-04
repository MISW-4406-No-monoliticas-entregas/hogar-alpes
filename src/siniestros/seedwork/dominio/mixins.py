"""Mixins de dominio."""
from seedwork.dominio.reglas import ReglaNegocio
from seedwork.dominio.excepciones import ReglaNegocioExcepcion


class ValidarReglasMixin:
    """Da a las entidades/agregados la capacidad de validar reglas de negocio.

    El agregado llama self.validar_regla(regla); si la regla no se cumple se
    lanza ReglaNegocioExcepcion. Así las invariantes viven dentro del dominio.
    """

    def validar_regla(self, regla: ReglaNegocio):
        if not regla.es_valido():
            raise ReglaNegocioExcepcion(regla)
