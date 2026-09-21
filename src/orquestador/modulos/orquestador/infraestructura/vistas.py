"""Vistas de lectura del Saga Log (lado de consulta)."""
from config.db import SessionLocal
from modulos.orquestador.aplicacion.dto import SagaDTO as SagaLecturaDTO
from modulos.orquestador.infraestructura.dto import SagaDTO


def _a_dto(fila) -> SagaLecturaDTO:
    return SagaLecturaDTO(
        id=fila.id,
        siniestro_id=fila.siniestro_id,
        paso_actual=fila.paso_actual,
        estado=fila.estado,
        proveedor_id=fila.proveedor_id,
        motivo_fallo=fila.motivo_fallo,
        partner_id=fila.partner_id,
        poliza=fila.poliza,
        servicio=fila.servicio,
        zona=fila.zona,
        fecha_creacion=fila.fecha_creacion.isoformat() if fila.fecha_creacion else None,
        fecha_actualizacion=(
            fila.fecha_actualizacion.isoformat() if fila.fecha_actualizacion else None
        ),
    )


def obtener_por_siniestro(siniestro_id: str) -> SagaLecturaDTO | None:
    session = SessionLocal()
    try:
        fila = (
            session.query(SagaDTO)
            .filter(SagaDTO.siniestro_id == siniestro_id)
            .order_by(SagaDTO.fecha_creacion.desc())
            .first()
        )
        return _a_dto(fila) if fila else None
    finally:
        session.close()


def obtener_por_id(id_saga: str) -> SagaLecturaDTO | None:
    session = SessionLocal()
    try:
        fila = session.get(SagaDTO, id_saga)
        return _a_dto(fila) if fila else None
    finally:
        session.close()


def listar(limite: int = 50) -> list[SagaLecturaDTO]:
    session = SessionLocal()
    try:
        filas = (
            session.query(SagaDTO)
            .order_by(SagaDTO.fecha_creacion.desc())
            .limit(limite)
            .all()
        )
        return [_a_dto(f) for f in filas]
    finally:
        session.close()
