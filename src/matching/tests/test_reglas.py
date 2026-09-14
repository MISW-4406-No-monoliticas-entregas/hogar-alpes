"""Pruebas del agregado Asignacion (dominio aislado, sin BD ni Pulsar)."""
import pytest

from seedwork.dominio.excepciones import ReglaNegocioExcepcion
from modulos.matching.dominio.entidades import ProveedorHabilitado
from modulos.matching.dominio.fabricas import FabricaAsignacion
from modulos.matching.dominio.objetos_valor import Servicio, Zona, EstadoAsignacion
from modulos.matching.dominio.eventos import ProveedorAsignado, SinProveedorDisponible


def _proveedor(nombre="Plomería Los Alpes"):
    return ProveedorHabilitado(
        nombre=nombre, servicio=Servicio("plomeria"), zona=Zona("norte")
    )


def test_asignar_con_proveedor_disponible_emite_proveedor_asignado():
    proveedor = _proveedor()
    asignacion = FabricaAsignacion().crear_asignacion(
        id_siniestro="s-1",
        servicio=Servicio("plomeria"),
        zona=Zona("norte"),
        proveedor=proveedor,
    )

    assert asignacion.estado == EstadoAsignacion.ASIGNADA
    assert asignacion.proveedor_id == str(proveedor.id)
    assert len(asignacion.eventos) == 1
    assert isinstance(asignacion.eventos[0], ProveedorAsignado)
    assert asignacion.eventos[0].id_siniestro == "s-1"


def test_asignar_sin_proveedor_emite_sin_proveedor_disponible():
    asignacion = FabricaAsignacion().crear_asignacion(
        id_siniestro="s-2",
        servicio=Servicio("vidrieria"),
        zona=Zona("sur"),
        proveedor=None,
    )

    assert asignacion.estado == EstadoAsignacion.SIN_PROVEEDOR
    assert asignacion.proveedor_id is None
    assert len(asignacion.eventos) == 1
    assert isinstance(asignacion.eventos[0], SinProveedorDisponible)


def test_id_siniestro_vacio_viola_regla():
    with pytest.raises(ReglaNegocioExcepcion):
        FabricaAsignacion().crear_asignacion(
            id_siniestro="   ",
            servicio=Servicio("plomeria"),
            zona=Zona("norte"),
            proveedor=_proveedor(),
        )


def test_liberar_una_asignacion_asignada_queda_liberada():
    asignacion = FabricaAsignacion().crear_asignacion(
        id_siniestro="s-3",
        servicio=Servicio("plomeria"),
        zona=Zona("norte"),
        proveedor=_proveedor(),
    )
    asignacion.limpiar_eventos()

    asignacion.liberar()

    assert asignacion.estado == EstadoAsignacion.LIBERADA
    assert asignacion.eventos == []  # sin evento de integración para la liberación


def test_no_se_puede_liberar_una_asignacion_sin_proveedor():
    asignacion = FabricaAsignacion().crear_asignacion(
        id_siniestro="s-4",
        servicio=Servicio("vidrieria"),
        zona=Zona("sur"),
        proveedor=None,
    )

    with pytest.raises(ReglaNegocioExcepcion):
        asignacion.liberar()


def test_marcar_ocupado_y_disponible_del_proveedor():
    proveedor = _proveedor()
    assert proveedor.disponible is True

    proveedor.marcar_ocupado()
    assert proveedor.disponible is False

    proveedor.marcar_disponible()
    assert proveedor.disponible is True
