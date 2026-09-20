"""Pruebas de infraestructura del Saga Log, contra SQLite en memoria.

No hay Postgres/docker en este slice todavía (ver README del módulo), pero
esto prueba con SQL real -- no un doble -- que la tabla `saga_log` existe,
se puede escribir por el repositorio y **consultar con SQL directo** (el
criterio de aceptación de esta pieza: "una consulta SQL directa a la tabla
del Saga Log muestra, para una saga dada, el paso actual y el estado").
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from config.db import Base
from modulos.orquestador.dominio.fabricas import FabricaSaga
from modulos.orquestador.infraestructura.dto import SagaDTO  # noqa: F401 (registra la tabla)
from modulos.orquestador.infraestructura.repositorios import RepositorioSagasSQLAlchemy


def _sesion_sqlite():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)()


def test_agregar_y_obtener_por_siniestro():
    session = _sesion_sqlite()
    repo = RepositorioSagasSQLAlchemy(session)
    saga = FabricaSaga().iniciar_saga("sin-100")

    repo.agregar(saga)
    session.commit()

    encontrada = repo.obtener_por_siniestro("sin-100")
    assert encontrada is not None
    assert encontrada.id == saga.id
    assert encontrada.paso_actual == saga.paso_actual


def test_actualizar_refleja_la_compensacion():
    session = _sesion_sqlite()
    repo = RepositorioSagasSQLAlchemy(session)
    saga = FabricaSaga().iniciar_saga("sin-101")
    repo.agregar(saga)
    session.commit()

    saga.compensar("Sin proveedor disponible")
    repo.actualizar(saga)
    session.commit()

    encontrada = repo.obtener_por_siniestro("sin-101")
    assert encontrada.paso_actual.value == "COMPENSANDO"
    assert encontrada.estado.value == "FALLIDO"
    assert encontrada.motivo_fallo == "Sin proveedor disponible"


def test_consulta_sql_directa_a_la_tabla_saga_log():
    """Ejercita literalmente el criterio de aceptación: SQL directo, sin
    pasar por el repositorio, para ver paso y estado de una saga dada."""
    session = _sesion_sqlite()
    repo = RepositorioSagasSQLAlchemy(session)
    saga = FabricaSaga().iniciar_saga("sin-102")
    repo.agregar(saga)
    session.commit()
    saga.compensar("Rechazado por reglas: monto excede el máximo")
    repo.actualizar(saga)
    session.commit()

    fila = session.execute(
        text(
            "SELECT paso_actual, estado, motivo_fallo FROM saga_log "
            "WHERE siniestro_id = :sid"
        ),
        {"sid": "sin-102"},
    ).one()

    assert fila.paso_actual == "COMPENSANDO"
    assert fila.estado == "FALLIDO"
    assert fila.motivo_fallo == "Rechazado por reglas: monto excede el máximo"
