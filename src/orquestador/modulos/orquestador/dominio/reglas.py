"""Reglas de negocio del módulo orquestador."""
from dataclasses import dataclass

from seedwork.dominio.reglas import ReglaNegocio
from modulos.orquestador.dominio.objetos_valor import EstadoSaga


@dataclass
class ElSiniestroEsObligatorio(ReglaNegocio):
    siniestro_id: str | None = None

    def __init__(self, siniestro_id, mensaje="La saga debe referenciar un siniestro"):
        super().__init__(mensaje)
        self.siniestro_id = siniestro_id

    def es_valido(self) -> bool:
        return self.siniestro_id is not None and bool(str(self.siniestro_id).strip())


@dataclass
class SoloSePuedeCompensarUnaSagaEnCurso(ReglaNegocio):
    estado: EstadoSaga | None = None

    def __init__(self, estado,
                 mensaje="Solo se puede compensar una saga que está EN_CURSO"):
        super().__init__(mensaje)
        self.estado = estado

    def es_valido(self) -> bool:
        return self.estado == EstadoSaga.EN_CURSO
