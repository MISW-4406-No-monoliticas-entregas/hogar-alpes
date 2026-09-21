"""Pruebas del camino feliz (C): el dominio y los cuatro comandos que avanzan
la saga, contra SQLite real y un despachador espia en vez de Pulsar.

Cubre las dos cosas que hay que poder demostrar en la sustentacion: que la
saga recorre PENDIENTE -> INICIADA -> VALIDANDO -> ASIGNANDO -> COMPLETADA
publicando un comando por paso, y que no se puede saltar pasos.
"""
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import config.db as config_db
import modulos.orquestador.aplicacion.servicios as servicios
import modulos.orquestador.aplicacion.handlers as handlers
from modulos.orquestador.aplicacion.comandos.pasos_felices import (
    IniciarSaga,
    IniciarSagaHandler,
    VincularSiniestro,
    VincularSiniestroHandler,
    AvanzarAAsignacion,
    AvanzarAAsignacionHandler,
    CompletarSaga,
    CompletarSagaHandler,
)
from modulos.orquestador.dominio.entidades import Saga
from modulos.orquestador.dominio.objetos_valor import PasoSaga, EstadoSaga
from modulos.orquestador.infraestructura.dto import SagaDTO
from modulos.orquestador.infraestructura import despachadores as despachadores_mod
from seedwork.dominio.excepciones import ReglaNegocioExcepcion

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
    llamadas = {"registrar": [], "validar": [], "marcar": [], "asignar": [], "cerrar": []}

    def _registrar(self, partner_id, poliza, monto, moneda, calle, ciudad, pais):
        llamadas["registrar"].append((partner_id, poliza, monto))

    def _validar(self, siniestro_id, partner_id, monto, moneda, servicio, zona):
        llamadas["validar"].append((siniestro_id, partner_id, monto, servicio, zona))

    def _marcar(self, siniestro_id):
        llamadas["marcar"].append(siniestro_id)

    def _asignar(self, siniestro_id, servicio, zona):
        llamadas["asignar"].append((siniestro_id, servicio, zona))

    def _cerrar(self, siniestro_id, proveedor_id):
        llamadas["cerrar"].append((siniestro_id, proveedor_id))

    d = despachadores_mod.DespachadorPasosFelices
    monkeypatch.setattr(d, "publicar_registrar_siniestro", _registrar)
    monkeypatch.setattr(d, "publicar_validar_siniestro", _validar)
    monkeypatch.setattr(d, "publicar_marcar_validado", _marcar)
    monkeypatch.setattr(d, "publicar_asignar_proveedor", _asignar)
    monkeypatch.setattr(d, "publicar_proveedor_asignado_a_siniestros", _cerrar)
    return llamadas


def _iniciar(poliza="POL-1", partner="seguros-alpes", servicio="plomeria",
             zona="bogota-norte", monto=500000.0):
    return IniciarSagaHandler().handle(
        IniciarSaga(
            partner_id=partner, poliza=poliza, monto=monto,
            servicio=servicio, zona=zona, moneda="COP",
            calle="Cra 7", ciudad="Bogota", pais="CO",
        )
    )


# --- dominio aislado, sin BD ni Pulsar --------------------------------------

def test_la_saga_nace_pendiente_sin_siniestro():
    saga = Saga()
    saga.iniciar_pendiente("seguros-alpes", "POL-9", "plomeria", "bogota-norte",
                           500000.0, "COP", "Cra 7", "Bogota", "CO")

    assert saga.paso_actual == PasoSaga.PENDIENTE
    assert saga.estado == EstadoSaga.EN_CURSO
    assert saga.siniestro_id is None
    assert saga.servicio == "plomeria"


def test_no_se_puede_saltar_de_pendiente_a_asignando():
    saga = Saga()
    saga.iniciar_pendiente("seguros-alpes", "POL-9", "plomeria", "bogota-norte",
                           500000.0, "COP", "Cra 7", "Bogota", "CO")

    with pytest.raises(ReglaNegocioExcepcion):
        saga.avanzar_a_asignando()


def test_no_se_puede_completar_sin_haber_pasado_por_asignando():
    saga = Saga()
    saga.iniciar_pendiente("seguros-alpes", "POL-9", "plomeria", "bogota-norte",
                           500000.0, "COP", "Cra 7", "Bogota", "CO")
    saga.vincular_siniestro("sin-1")

    with pytest.raises(ReglaNegocioExcepcion):
        saga.completar()


def test_la_secuencia_completa_deja_la_saga_en_ok():
    saga = Saga()
    saga.iniciar_pendiente("seguros-alpes", "POL-9", "plomeria", "bogota-norte",
                           500000.0, "COP", "Cra 7", "Bogota", "CO")
    saga.vincular_siniestro("sin-1")
    saga.avanzar_a_validando(500000.0, "COP")
    saga.avanzar_a_asignando()
    saga.registrar_proveedor_reservado("prov-3")
    saga.completar()

    assert saga.paso_actual == PasoSaga.COMPLETADA
    assert saga.estado == EstadoSaga.OK


# --- comandos completos: UoW + repositorio + despachador --------------------

def test_iniciar_saga_publica_registrar_siniestro(sesion_sqlite, despachador_de_prueba):
    id_saga = _iniciar(poliza="POL-100")

    assert id_saga is not None
    assert despachador_de_prueba["registrar"] == [("seguros-alpes", "POL-100", 500000.0)]

    fila = sesion_sqlite().get(SagaDTO, id_saga)
    assert fila.paso_actual == "PENDIENTE"
    assert fila.siniestro_id is None


def test_vincular_correlaciona_por_partner_y_poliza_y_pide_validacion(
    sesion_sqlite, despachador_de_prueba
):
    id_saga = _iniciar(poliza="POL-101")

    VincularSiniestroHandler().handle(
        VincularSiniestro(
            partner_id="seguros-alpes", poliza="POL-101",
            siniestro_id="sin-101", monto=500000.0, moneda="COP",
        )
    )

    assert despachador_de_prueba["validar"] == [
        ("sin-101", "seguros-alpes", 500000.0, "plomeria", "bogota-norte")
    ]
    fila = sesion_sqlite().get(SagaDTO, id_saga)
    assert fila.paso_actual == "VALIDANDO"
    assert fila.siniestro_id == "sin-101"


def test_un_siniestro_ajeno_no_crea_ni_toca_sagas(sesion_sqlite, despachador_de_prueba):
    """Un SiniestroRegistrado que no arranco el orquestador se ignora."""
    resultado = VincularSiniestroHandler().handle(
        VincularSiniestro(
            partner_id="otro-partner", poliza="POL-AJENA",
            siniestro_id="sin-999", monto=1.0, moneda="COP",
        )
    )

    assert resultado is None
    assert despachador_de_prueba["validar"] == []
    assert sesion_sqlite().query(SagaDTO).count() == 0


def test_aprobacion_de_reglas_pide_proveedor_y_confirma_a_siniestros(
    sesion_sqlite, despachador_de_prueba
):
    _iniciar(poliza="POL-102")
    VincularSiniestroHandler().handle(
        VincularSiniestro(partner_id="seguros-alpes", poliza="POL-102",
                          siniestro_id="sin-102", monto=500000.0)
    )

    AvanzarAAsignacionHandler().handle(
        AvanzarAAsignacion(siniestro_id="sin-102", servicio="plomeria",
                           zona="bogota-norte")
    )

    assert despachador_de_prueba["marcar"] == ["sin-102"]
    assert despachador_de_prueba["asignar"] == [("sin-102", "plomeria", "bogota-norte")]


def test_camino_feliz_de_punta_a_punta(sesion_sqlite, despachador_de_prueba):
    from modulos.orquestador.aplicacion.comandos.compensaciones import (
        RegistrarProveedorAsignado,
        RegistrarProveedorAsignadoHandler,
    )

    id_saga = _iniciar(poliza="POL-103")
    VincularSiniestroHandler().handle(
        VincularSiniestro(partner_id="seguros-alpes", poliza="POL-103",
                          siniestro_id="sin-103", monto=500000.0)
    )
    AvanzarAAsignacionHandler().handle(
        AvanzarAAsignacion(siniestro_id="sin-103", servicio="plomeria",
                           zona="bogota-norte")
    )
    RegistrarProveedorAsignadoHandler().handle(
        RegistrarProveedorAsignado(siniestro_id="sin-103", proveedor_id="prov-5")
    )
    CompletarSagaHandler().handle(CompletarSaga(siniestro_id="sin-103"))

    assert despachador_de_prueba["cerrar"] == [("sin-103", "prov-5")]

    session = sesion_sqlite()
    fila = session.get(SagaDTO, id_saga)
    assert fila.paso_actual == "COMPLETADA"
    assert fila.estado == "OK"
    assert fila.proveedor_id == "prov-5"


def test_consulta_sql_directa_muestra_el_recorrido(sesion_sqlite, despachador_de_prueba):
    """El criterio de aceptacion del Saga Log, del lado del camino feliz."""
    _iniciar(poliza="POL-104")
    VincularSiniestroHandler().handle(
        VincularSiniestro(partner_id="seguros-alpes", poliza="POL-104",
                          siniestro_id="sin-104", monto=500000.0)
    )

    session = sesion_sqlite()
    fila = session.execute(
        text("SELECT paso_actual, estado, servicio, zona FROM saga_log "
             "WHERE siniestro_id = :sid"),
        {"sid": "sin-104"},
    ).first()

    assert fila.paso_actual == "VALIDANDO"
    assert fila.estado == "EN_CURSO"
    assert fila.servicio == "plomeria"


def test_vincular_es_idempotente_por_id_mensaje(sesion_sqlite, despachador_de_prueba):
    _iniciar(poliza="POL-105")

    VincularSiniestroHandler().handle(
        VincularSiniestro(partner_id="seguros-alpes", poliza="POL-105",
                          siniestro_id="sin-105", monto=500000.0, id_mensaje="msg-9")
    )
    resultado = VincularSiniestroHandler().handle(
        VincularSiniestro(partner_id="seguros-alpes", poliza="POL-105",
                          siniestro_id="sin-105", monto=500000.0, id_mensaje="msg-9")
    )

    assert resultado is None
    assert len(despachador_de_prueba["validar"]) == 1


def test_la_saga_en_validando_se_puede_compensar(sesion_sqlite, despachador_de_prueba,
                                                 monkeypatch):
    """El camino de fallo de D engancha en cualquier punto del camino feliz."""
    from modulos.orquestador.aplicacion.comandos.compensaciones import (
        CompensarSaga,
        CompensarSagaHandler,
    )

    rechazos = []
    monkeypatch.setattr(
        despachadores_mod.DespachadorCompensaciones,
        "publicar_rechazar_siniestro",
        lambda self, siniestro_id, motivo: rechazos.append((siniestro_id, motivo)),
    )

    id_saga = _iniciar(poliza="POL-106")
    VincularSiniestroHandler().handle(
        VincularSiniestro(partner_id="seguros-alpes", poliza="POL-106",
                          siniestro_id="sin-106", monto=500000.0)
    )

    CompensarSagaHandler().handle(
        CompensarSaga(siniestro_id="sin-106", motivo="Rechazado por reglas: monto")
    )

    fila = sesion_sqlite().get(SagaDTO, id_saga)
    assert fila.paso_actual == "COMPENSADA"
    assert fila.estado == "FALLIDO"
    assert rechazos == [("sin-106", "Rechazado por reglas: monto")]
