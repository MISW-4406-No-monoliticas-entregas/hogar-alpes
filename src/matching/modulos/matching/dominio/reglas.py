"""Reglas de negocio del módulo matching."""
from dataclasses import dataclass

from seedwork.dominio.reglas import ReglaNegocio
from modulos.matching.dominio.objetos_valor import EstadoAsignacion


@dataclass
class ElSiniestroEsObligatorio(ReglaNegocio):
    id_siniestro: str | None = None

    def __init__(self, id_siniestro, mensaje="La asignación debe referenciar un siniestro"):
        super().__init__(mensaje)
        self.id_siniestro = id_siniestro

    def es_valido(self) -> bool:
        return self.id_siniestro is not None and bool(str(self.id_siniestro).strip())


@dataclass
class LaAsignacionDebeEstarAsignadaParaLiberar(ReglaNegocio):
    estado: EstadoAsignacion | None = None

    def __init__(self, estado,
                 mensaje="Solo se puede liberar una asignación en estado ASIGNADA"):
        super().__init__(mensaje)
        self.estado = estado

    def es_valido(self) -> bool:
        return self.estado == EstadoAsignacion.ASIGNADA
