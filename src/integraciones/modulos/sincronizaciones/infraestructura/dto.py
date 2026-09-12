"""Modelo SQLAlchemy de la tabla sincronizaciones (CRUD)."""
from sqlalchemy import Column, String, BigInteger, UniqueConstraint

from config.db import Base


class SincronizacionDTO(Base):
    __tablename__ = "sincronizaciones"
    # Idempotencia de negocio a nivel de BD: no se recibe dos veces el mismo
    # siniestro de un partner (además del chequeo en el handler).
    __table_args__ = (
        UniqueConstraint("partner_id", "id_externo", name="uq_partner_id_externo"),
    )

    id = Column(String(36), primary_key=True)
    partner_id = Column(String(100), nullable=False, index=True)
    id_externo = Column(String(100), nullable=False)
    id_siniestro = Column(String(36), nullable=True)  # se llena en la E5 (saga)
    estado = Column(String(20), nullable=False)
    recibido_en = Column(BigInteger, nullable=False)
    publicado_en = Column(BigInteger, nullable=True)
