"""Vistas de lectura del módulo sincronizaciones (lado de consulta)."""
from config.db import SessionLocal
from modulos.sincronizaciones.aplicacion.dto import SincronizacionDTO as DTOLectura
from modulos.sincronizaciones.infraestructura.dto import SincronizacionDTO


def _a_dto(fila: SincronizacionDTO) -> DTOLectura:
    return DTOLectura(
        id=fila.id,
        partner_id=fila.partner_id,
        id_externo=fila.id_externo,
        id_siniestro=fila.id_siniestro,
        estado=fila.estado,
        recibido_en=fila.recibido_en,
        publicado_en=fila.publicado_en,
    )


def obtener(id_sincronizacion: str) -> DTOLectura | None:
    session = SessionLocal()
    try:
        fila = session.get(SincronizacionDTO, id_sincronizacion)
        return _a_dto(fila) if fila else None
    finally:
        session.close()


def listar_por_partner(partner_id: str) -> list[DTOLectura]:
    session = SessionLocal()
    try:
        filas = (
            session.query(SincronizacionDTO)
            .filter_by(partner_id=partner_id)
            .order_by(SincronizacionDTO.recibido_en.desc())
            .all()
        )
        return [_a_dto(f) for f in filas]
    finally:
        session.close()
