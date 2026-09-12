"""Pruebas unitarias de las reglas de negocio del agregado Siniestro."""
import pytest

from seedwork.dominio.excepciones import ReglaNegocioExcepcion
from modulos.siniestros.dominio.fabricas import FabricaSiniestro
from modulos.siniestros.dominio.entidades import Siniestro
from modulos.siniestros.dominio.objetos_valor import (
    PartnerId,
    Poliza,
    Monto,
    Direccion,
    EstadoSiniestro,
)
from modulos.siniestros.dominio.eventos import (
    SiniestroRegistrado,
    ProveedorAsignado,
)


def _valores(monto=1000.0, poliza="POL-1"):
    return dict(
        partner_id=PartnerId("partner-1"),
        poliza=Poliza(poliza),
        monto=Monto(monto),
        direccion=Direccion("Calle 1", "Bogota"),
    )


@pytest.fixture
def fabrica():
    return FabricaSiniestro()


def test_registrar_siniestro_valido_queda_registrado(fabrica):
    s = fabrica.crear_siniestro(**_valores())
    assert s.estado == EstadoSiniestro.REGISTRADO


def test_registrar_emite_evento_siniestro_registrado(fabrica):
    s = fabrica.crear_siniestro(**_valores())
    eventos = [type(e) for e in s.eventos]
    assert SiniestroRegistrado in eventos


def test_monto_no_positivo_viola_regla(fabrica):
    with pytest.raises(ReglaNegocioExcepcion):
        fabrica.crear_siniestro(**_valores(monto=0))
    with pytest.raises(ReglaNegocioExcepcion):
        fabrica.crear_siniestro(**_valores(monto=-5))


def test_poliza_vacia_viola_regla(fabrica):
    with pytest.raises(ReglaNegocioExcepcion):
        fabrica.crear_siniestro(**_valores(poliza="   "))


def test_asignar_proveedor_desde_registrado(fabrica):
    s = fabrica.crear_siniestro(**_valores())
    s.limpiar_eventos()
    s.asignar_proveedor("prov-99")
    assert s.estado == EstadoSiniestro.ASIGNADO
    assert s.proveedor_id == "prov-99"
    assert any(isinstance(e, ProveedorAsignado) for e in s.eventos)


def test_no_se_puede_asignar_dos_veces(fabrica):
    s = fabrica.crear_siniestro(**_valores())
    s.asignar_proveedor("prov-1")
    with pytest.raises(ReglaNegocioExcepcion):
        s.asignar_proveedor("prov-2")


def test_no_se_puede_asignar_si_no_esta_registrado():
    """Estado ASIGNADO desde el inicio: no cumple la precondición."""
    s = Siniestro(**_valores(), estado=EstadoSiniestro.ASIGNADO)
    with pytest.raises(ReglaNegocioExcepcion):
        s.asignar_proveedor("prov-1")
