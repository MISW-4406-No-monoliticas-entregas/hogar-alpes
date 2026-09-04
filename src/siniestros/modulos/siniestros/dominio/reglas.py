"""Reglas de negocio del agregado Siniestro.

Cada regla es un objeto con es_valido(); el agregado las valida con
self.validar_regla(...). Se prueban unitariamente en tests/test_reglas.py.
"""
from dataclasses import dataclass

from seedwork.dominio.reglas import ReglaNegocio
from modulos.siniestros.dominio.objetos_valor import (
    Monto,
    Poliza,
    EstadoSiniestro,
)


@dataclass
class LaPolizaEsObligatoria(ReglaNegocio):
    poliza: Poliza | None = None

    def __init__(self, poliza, mensaje="El siniestro debe tener una póliza asociada"):
        super().__init__(mensaje)
        self.poliza = poliza

    def es_valido(self) -> bool:
        return self.poliza is not None and bool(self.poliza.numero.strip())


@dataclass
class ElMontoEstimadoDebeSerPositivo(ReglaNegocio):
    monto: Monto | None = None

    def __init__(self, monto, mensaje="El monto estimado debe ser positivo"):
        super().__init__(mensaje)
        self.monto = monto

    def es_valido(self) -> bool:
        return self.monto is not None and self.monto.valor > 0


@dataclass
class ElSiniestroDebeEstarRegistradoParaAsignar(ReglaNegocio):
    estado: EstadoSiniestro | None = None

    def __init__(self, estado,
                 mensaje="Un siniestro solo puede asignarse si está en estado REGISTRADO"):
        super().__init__(mensaje)
        self.estado = estado

    def es_valido(self) -> bool:
        return self.estado == EstadoSiniestro.REGISTRADO
