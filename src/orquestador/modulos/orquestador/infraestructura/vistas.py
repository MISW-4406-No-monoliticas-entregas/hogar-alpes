"""Vistas de lectura del Saga Log (lado de consulta)."""
from config.db import SessionLocal
from modulos.orquestador.aplicacion.dto import SagaDTO as SagaLecturaDTO
from modulos.orquestador.infraestructura.dto import SagaDTO


def obtener_por_siniestro(siniestro_id: str) -> SagaLecturaDTO | None:
    session = SessionLocal()
    try:
        fila = (
            session.query(SagaDTO)
            .filter(SagaDTO.siniestro_id == siniestro_id)
            .order_by(SagaDTO.fecha_creacion.desc())
            .first()
        )
        if fila is None:
            return None
        return SagaLecturaDTO(
            id=fila.id,
            siniestro_id=fila.siniestro_id,
            paso_actual=fila.paso_actual,
            estado=fila.estado,
            proveedor_id=fila.proveedor_id,
            motivo_fallo=fila.motivo_fallo,
        )
    finally:
        session.close()
