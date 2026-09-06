"""Vistas de lectura sobre la proyección estado_siniestro."""
from modulos.seguimiento.infraestructura.repositorios import (
    RepositorioEstadoSiniestro,
)
from modulos.seguimiento.dominio.entidades import EstadoDeSiniestro

_repositorio = RepositorioEstadoSiniestro()


def _a_modelo_lectura(fila) -> EstadoDeSiniestro:
    return EstadoDeSiniestro(
        id_siniestro=fila.id_siniestro,
        partner_id=fila.partner_id,
        estado=fila.estado,
        poliza=fila.poliza,
        monto=fila.monto,
        moneda=fila.moneda,
        proveedor_id=fila.proveedor_id,
        fecha_actualizacion=fila.fecha_actualizacion,
    )


def obtener_estado(id_siniestro: str) -> EstadoDeSiniestro | None:
    fila = _repositorio.obtener_por_id(id_siniestro)
    return _a_modelo_lectura(fila) if fila else None


def listar_por_partner(partner_id: str) -> list[EstadoDeSiniestro]:
    return [_a_modelo_lectura(f) for f in _repositorio.listar_por_partner(partner_id)]
