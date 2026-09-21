"""Pruebas de integración de compensaciones.py (aplicación), contra SQLite en
memoria y un despachador de prueba (sin Pulsar real).

No hay servicio corriendo en este slice (ver README), así que esto es lo más
cerca de un end-to-end que se puede probar sin Docker: ejercita el comando,
la Unidad de Trabajo, el repositorio (SQL real) y el despachador de eventos
de dominio tal como los usaría el consumidor real.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import config.db as config_db
import modulos.orquestador.aplicacion.servicios as servicios
import modulos.orquestador.aplicacion.handlers as handlers
from modulos.orquestador.aplicacion.comandos.compensaciones import (
    CompensarSaga,
    CompensarSagaHandler,
    RegistrarProveedorAsignado,
    RegistrarProveedorAsignadoHandler,
)
from modulos.orquestador.infraestructura.dto import SagaDTO
from modulos.orquestador.infraestructura import despachadores as despachadores_mod

# Se registra una sola vez para todo el módulo (PyDispatcher es global).
handlers.registrar_handlers()


@pytest.fixture()
def sesion_sqlite(monkeypatch):
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    config_db.Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    monkeypatch.setattr(servicios, "SessionLocal", Session)
    return Session


@pytest.fixture()
def despachador_de_prueba(monkeypatch):
    """Reemplaza las publicaciones a Pulsar por un espía en memoria."""
    llamadas = {"rechazar": [], "liberar": []}

    def _rechazar(self, siniestro_id, motivo):
        llamadas["rechazar"].append((siniestro_id, motivo))

    def _liberar(self, siniestro_id, proveedor_id):
        llamadas["liberar"].append((siniestro_id, proveedor_id))

    monkeypatch.setattr(
        despachadores_mod.DespachadorCompensaciones,
        "publicar_rechazar_siniestro", _rechazar,
    )
    monkeypatch.setattr(
        despachadores_mod.DespachadorCompensaciones,
        "publicar_liberar_proveedor", _liberar,
    )
    return llamadas


def test_compensar_sin_proveedor_reservado_solo_rechaza(sesion_sqlite, despachador_de_prueba):
    CompensarSagaHandler().handle(
        CompensarSaga(siniestro_id="sin-200", motivo="Sin proveedor disponible")
    )

    assert despachador_de_prueba["rechazar"] == [("sin-200", "Sin proveedor disponible")]
    assert despachador_de_prueba["liberar"] == []


def test_compensar_con_proveedor_reservado_tambien_libera(sesion_sqlite, despachador_de_prueba):
    RegistrarProveedorAsignadoHandler().handle(
        RegistrarProveedorAsignado(siniestro_id="sin-201", proveedor_id="prov-7")
    )

    CompensarSagaHandler().handle(
        CompensarSaga(siniestro_id="sin-201", motivo="Falló un paso posterior")
    )

    assert despachador_de_prueba["rechazar"] == [("sin-201", "Falló un paso posterior")]
    assert despachador_de_prueba["liberar"] == [("sin-201", "prov-7")]


def test_compensar_deja_la_fila_en_compensada(sesion_sqlite, despachador_de_prueba):
    id_saga = CompensarSagaHandler().handle(
        CompensarSaga(siniestro_id="sin-202", motivo="motivo")
    )

    session = sesion_sqlite()
    fila = session.get(SagaDTO, id_saga)
    assert fila.paso_actual == "COMPENSADA"
    assert fila.estado == "FALLIDO"


def test_compensar_es_idempotente_por_id_mensaje(sesion_sqlite, despachador_de_prueba):
    CompensarSagaHandler().handle(
        CompensarSaga(siniestro_id="sin-203", motivo="motivo", id_mensaje="msg-1")
    )
    resultado = CompensarSagaHandler().handle(
        CompensarSaga(siniestro_id="sin-203", motivo="motivo", id_mensaje="msg-1")
    )

    assert resultado is None  # ya procesado; el consumidor real haría ack sin repetir
    assert len(despachador_de_prueba["rechazar"]) == 1  # no se publicó dos veces


def test_compensar_sin_saga_previa_la_crea_para_no_perder_el_fallo(
    sesion_sqlite, despachador_de_prueba
):
    """Simula correr esta pieza aislada (sin el camino feliz de C todavía)."""
    id_saga = CompensarSagaHandler().handle(
        CompensarSaga(siniestro_id="sin-204", motivo="prueba aislada")
    )

    assert id_saga is not None
    assert despachador_de_prueba["rechazar"] == [("sin-204", "prueba aislada")]
