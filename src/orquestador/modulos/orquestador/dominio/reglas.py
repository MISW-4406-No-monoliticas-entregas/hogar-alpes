"""Reglas de negocio del modulo orquestador."""
from dataclasses import dataclass

from seedwork.dominio.reglas import ReglaNegocio
from modulos.orquestador.dominio.objetos_valor import EstadoSaga, PasoSaga


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


@dataclass
class ElPartnerYLaPolizaSonObligatorios(ReglaNegocio):
    partner_id: str | None = None
    poliza: str | None = None

    def __init__(self, partner_id, poliza,
                 mensaje="La saga necesita partner_id y poliza para correlacionar"):
        super().__init__(mensaje)
        self.partner_id = partner_id
        self.poliza = poliza

    def es_valido(self) -> bool:
        return bool(str(self.partner_id or "").strip()) and bool(str(self.poliza or "").strip())


@dataclass
class LaSagaDebeEstarEnElPasoEsperado(ReglaNegocio):
    """Impide saltarse pasos: cada avance solo es valido desde el anterior."""
    paso_actual: PasoSaga | None = None
    pasos_validos: tuple = ()

    def __init__(self, paso_actual, pasos_validos, mensaje=None):
        esperados = ", ".join(p.value for p in pasos_validos)
        super().__init__(
            mensaje or f"La saga esta en {paso_actual} y solo puede avanzar desde {esperados}"
        )
        self.paso_actual = paso_actual
        self.pasos_validos = tuple(pasos_validos)

    def es_valido(self) -> bool:
        return self.paso_actual in self.pasos_validos
