"""Pruebas del event store: replay, versiones y conflicto de concurrencia.

Usan SQLite en memoria con los mismos modelos SQLAlchemy: el contrato que se
prueba (insertar eventos, constraint único (siniestro_id, version), replay en
orden) es el mismo que en PostgreSQL.
"""
import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config.db import Base
from modulos.siniestros.dominio.entidades import Siniestro
from modulos.siniestros.dominio.excepciones import ConflictoDeConcurrencia
from modulos.siniestros.dominio.fabricas import FabricaSiniestro
from modulos.siniestros.dominio.objetos_valor import (
    PartnerId,
    Poliza,
    Monto,
    Direccion,
    EstadoSiniestro,
)
from modulos.siniestros.infraestructura.dto import EventoSiniestroDTO
from modulos.siniestros.infraestructura.repositorios import (
    RepositorioSiniestrosEventStore,
)
from modulos.siniestros.infraestructura.mapeadores_eventos import (
    evento_a_dict,
    dict_a_evento,
)


@pytest.fixture
def session():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()


def _nuevo_siniestro() -> Siniestro:
    return FabricaSiniestro().crear_siniestro(
        partner_id=PartnerId("partner-1"),
        poliza=Poliza("POL-1"),
        monto=Monto(1000.0, "COP"),
        direccion=Direccion("Calle 1", "Bogotá", "CO"),
    )


def test_agregar_guarda_los_eventos_con_version_incremental(session):
    repo = RepositorioSiniestrosEventStore(session)
    siniestro = _nuevo_siniestro()

    repo.agregar(siniestro)
    session.commit()

    filas = session.query(EventoSiniestroDTO).all()
    assert [(f.tipo, f.version) for f in filas] == [("SiniestroRegistrado", 1)]
    assert filas[0].siniestro_id == str(siniestro.id)
    assert filas[0].datos["partner_id"] == "partner-1"
    assert filas[0].datos["ciudad"] == "Bogotá"  # la dirección viaja en el evento


def test_replay_reconstruye_el_agregado_sin_revalidar(session):
    repo = RepositorioSiniestrosEventStore(session)
    siniestro = _nuevo_siniestro()
    repo.agregar(siniestro)
    siniestro.limpiar_eventos()
    session.commit()

    releido = repo.obtener_por_id(siniestro.id)
    releido.asignar_proveedor("prov-7")
    repo.actualizar(releido)
    releido.limpiar_eventos()
    session.commit()

    releido2 = repo.obtener_por_id(siniestro.id)
    releido2.marcar_validado()
    repo.actualizar(releido2)
    releido2.limpiar_eventos()
    session.commit()

    final = repo.obtener_por_id(siniestro.id)
    assert final.estado == EstadoSiniestro.VALIDADO
    assert final.proveedor_id == "prov-7"
    assert final.partner_id == PartnerId("partner-1")
    assert final.direccion == Direccion("Calle 1", "Bogotá", "CO")
    assert final._version_almacenada == 3
    assert final.eventos == []  # el replay no emite eventos nuevos

    versiones = [
        (f.tipo, f.version)
        for f in session.query(EventoSiniestroDTO)
        .filter_by(siniestro_id=str(siniestro.id))
        .order_by(EventoSiniestroDTO.version)
    ]
    assert versiones == [
        ("SiniestroRegistrado", 1),
        ("ProveedorAsignado", 2),
        ("SiniestroValidado", 3),
    ]


def test_conflicto_de_concurrencia_no_se_silencia(session):
    repo = RepositorioSiniestrosEventStore(session)
    siniestro = _nuevo_siniestro()
    repo.agregar(siniestro)
    siniestro.limpiar_eventos()
    session.commit()

    # Dos "procesos" cargan la misma versión y ambos intentan escribir la 2.
    copia_a = repo.obtener_por_id(siniestro.id)
    copia_b = repo.obtener_por_id(siniestro.id)

    copia_a.asignar_proveedor("prov-1")
    repo.actualizar(copia_a)
    copia_a.limpiar_eventos()
    session.commit()

    copia_b.asignar_proveedor("prov-2")
    with pytest.raises(ConflictoDeConcurrencia):
        repo.actualizar(copia_b)


def test_rechazar_se_reproduce_con_motivo(session):
    repo = RepositorioSiniestrosEventStore(session)
    siniestro = _nuevo_siniestro()
    siniestro.rechazar("fraude_sospechado")
    repo.agregar(siniestro)
    siniestro.limpiar_eventos()
    session.commit()

    releido = repo.obtener_por_id(siniestro.id)
    assert releido.estado == EstadoSiniestro.RECHAZADO
    assert releido.motivo_rechazo == "fraude_sospechado"


def test_serializacion_de_eventos_ida_y_vuelta():
    siniestro = _nuevo_siniestro()
    evento = siniestro.eventos[0]

    datos = evento_a_dict(evento)
    assert isinstance(datos["id"], str)  # JSON-seguro

    reconstruido = dict_a_evento("SiniestroRegistrado", datos)
    assert reconstruido.partner_id == evento.partner_id
    assert reconstruido.monto == evento.monto
    assert reconstruido.id == evento.id
    assert reconstruido.fecha_evento == evento.fecha_evento


def test_dict_a_evento_ignora_campos_desconocidos():
    datos = {"id_siniestro": "abc", "estado": "VALIDADO", "campo_viejo": "x"}
    evento = dict_a_evento("SiniestroValidado", datos)
    assert evento.estado == "VALIDADO"
