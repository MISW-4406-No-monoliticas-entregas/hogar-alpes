"""Pruebas del agregado Saga (dominio aislado, sin BD ni Pulsar).

Cubren el camino de fallo (D): compensar según corresponda, y la invariante
de que solo se compensa una saga EN_CURSO.
"""
import pytest

from seedwork.dominio.excepciones import ReglaNegocioExcepcion
from modulos.orquestador.dominio.entidades import Saga
from modulos.orquestador.dominio.objetos_valor import PasoSaga, EstadoSaga
from modulos.orquestador.dominio.eventos import CompensacionIniciada


def test_iniciar_saga_queda_en_curso():
    saga = Saga()
    saga.iniciar("sin-1")

    assert saga.paso_actual == PasoSaga.INICIADA
    assert saga.estado == EstadoSaga.EN_CURSO
    assert saga.siniestro_id == "sin-1"


def test_siniestro_vacio_viola_regla():
    with pytest.raises(ReglaNegocioExcepcion):
        Saga().iniciar("   ")


def test_compensar_sin_proveedor_reservado_no_pide_liberar():
    """Caso real: SiniestroRechazadoPorReglas o SinProveedorDisponible sin
    que nunca se haya reservado un proveedor -- solo hay que rechazar."""
    saga = Saga()
    saga.iniciar("sin-2")
    saga.limpiar_eventos()

    saga.compensar("Sin proveedor disponible para el servicio/zona solicitados")

    assert saga.paso_actual == PasoSaga.COMPENSANDO
    assert saga.estado == EstadoSaga.FALLIDO
    assert saga.motivo_fallo == "Sin proveedor disponible para el servicio/zona solicitados"
    assert len(saga.eventos) == 1
    evento = saga.eventos[0]
    assert isinstance(evento, CompensacionIniciada)
    assert evento.siniestro_id == "sin-2"
    assert evento.proveedor_id is None


def test_compensar_con_proveedor_reservado_pide_liberarlo():
    """Si la saga ya había anotado un proveedor (S7 lo confirmó) y algo
    posterior falla, la compensación debe incluirlo para liberarlo."""
    saga = Saga()
    saga.iniciar("sin-3")
    saga.registrar_proveedor_reservado("prov-9")
    saga.limpiar_eventos()

    saga.compensar("Falló un paso posterior a la asignación")

    evento = saga.eventos[0]
    assert evento.proveedor_id == "prov-9"


def test_no_se_puede_compensar_una_saga_que_no_esta_en_curso():
    saga = Saga()
    saga.iniciar("sin-4")
    saga.compensar("primer fallo")  # ahora está FALLIDO/COMPENSANDO

    with pytest.raises(ReglaNegocioExcepcion):
        saga.compensar("segundo fallo")


def test_completar_compensacion_queda_compensada():
    saga = Saga()
    saga.iniciar("sin-5")
    saga.compensar("motivo")

    saga.completar_compensacion()

    assert saga.paso_actual == PasoSaga.COMPENSADA
    # El estado del desenlace se queda en FALLIDO; COMPENSADA es del paso.
    assert saga.estado == EstadoSaga.FALLIDO
