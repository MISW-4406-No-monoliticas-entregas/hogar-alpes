"""Excepciones específicas del dominio de matching."""
from seedwork.dominio.excepciones import ExcepcionDominio


class AsignacionNoExiste(ExcepcionDominio):
    def __init__(self, id_siniestro):
        super().__init__(f"No existe una asignación activa para el siniestro {id_siniestro}")
