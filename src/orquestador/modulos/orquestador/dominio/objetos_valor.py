"""Objetos valor del módulo orquestador (el Saga Log)."""
from enum import Enum


class PasoSaga(str, Enum):
    """En qué paso de la transacción larga va la saga."""
    INICIADA = "INICIADA"
    VALIDANDO = "VALIDANDO"
    ASIGNANDO = "ASIGNANDO"
    COMPLETADA = "COMPLETADA"
    COMPENSANDO = "COMPENSANDO"
    COMPENSADA = "COMPENSADA"


class EstadoSaga(str, Enum):
    """Desenlace de la saga, independiente del paso en el que esté."""
    EN_CURSO = "EN_CURSO"
    OK = "OK"
    FALLIDO = "FALLIDO"
