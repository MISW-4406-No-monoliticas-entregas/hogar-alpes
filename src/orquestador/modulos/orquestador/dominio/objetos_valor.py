"""Objetos valor del modulo orquestador (el Saga Log)."""
from enum import Enum


class PasoSaga(str, Enum):
    """En que paso de la transaccion larga va la saga.

    PENDIENTE es el paso previo a INICIADA: la saga ya existe con los datos de
    negocio (partner, poliza, servicio, zona) pero todavia no conoce el
    id_siniestro, porque quien lo genera es S2 al procesar RegistrarSiniestro.
    """
    PENDIENTE = "PENDIENTE"
    INICIADA = "INICIADA"
    VALIDANDO = "VALIDANDO"
    ASIGNANDO = "ASIGNANDO"
    COMPLETADA = "COMPLETADA"
    COMPENSANDO = "COMPENSANDO"
    COMPENSADA = "COMPENSADA"


class EstadoSaga(str, Enum):
    """Desenlace de la saga, independiente del paso en el que este."""
    EN_CURSO = "EN_CURSO"
    OK = "OK"
    FALLIDO = "FALLIDO"
