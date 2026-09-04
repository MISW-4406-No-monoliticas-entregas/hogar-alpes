"""Excepciones específicas del dominio de siniestros."""
from seedwork.dominio.excepciones import ExcepcionDominio


class SiniestroNoExiste(ExcepcionDominio):
    def __init__(self, id_siniestro):
        super().__init__(f"No existe el siniestro {id_siniestro}")
