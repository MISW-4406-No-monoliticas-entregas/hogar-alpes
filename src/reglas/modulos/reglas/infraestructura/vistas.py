"""Vistas de lectura del modulo reglas."""
from config.db import SessionLocal
from modulos.reglas.aplicacion.dto import ReglaDePartnerDTO as ReglaLecturaDTO
from modulos.reglas.aplicacion.dto import ValidacionDTO as ValidacionLecturaDTO
from modulos.reglas.infraestructura.dto import ReglaDePartnerDTO, ValidacionDTO
from modulos.reglas.infraestructura.mapeadores import _partir


def obtener_reglas(partner_id: str) -> ReglaLecturaDTO | None:
    session = SessionLocal()
    try:
        fila = (
            session.query(ReglaDePartnerDTO)
            .filter(ReglaDePartnerDTO.partner_id == partner_id)
            .one_or_none()
        )
        if fila is None:
            return None
        return ReglaLecturaDTO(
            partner_id=fila.partner_id,
            monto_maximo=fila.monto_maximo,
            moneda=fila.moneda,
            servicios_cubiertos=_partir(fila.servicios_cubiertos),
            zonas_habilitadas=_partir(fila.zonas_habilitadas),
            activa=fila.activa,
        )
    finally:
        session.close()


def listar_validaciones(partner_id: str, limite: int = 50) -> list[ValidacionLecturaDTO]:
    session = SessionLocal()
    try:
        filas = (
            session.query(ValidacionDTO)
            .filter(ValidacionDTO.partner_id == partner_id)
            .order_by(ValidacionDTO.fecha_creacion.desc())
            .limit(limite)
            .all()
        )
        return [
            ValidacionLecturaDTO(
                id=f.id,
                id_siniestro=f.id_siniestro,
                partner_id=f.partner_id,
                monto=f.monto,
                moneda=f.moneda,
                servicio=f.servicio,
                zona=f.zona,
                resultado=f.resultado,
                motivo=f.motivo,
                fecha=f.fecha_creacion.isoformat(),
            )
            for f in filas
        ]
    finally:
        session.close()
