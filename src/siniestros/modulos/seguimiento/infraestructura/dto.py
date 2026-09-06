"""Modelo SQLAlchemy de la tabla estado_siniestro (proyección)."""
from sqlalchemy import Column, String, Float, DateTime

from config.db import Base


class EstadoSiniestroDTO(Base):
    __tablename__ = "estado_siniestro"

    id_siniestro = Column(String(36), primary_key=True)
    partner_id = Column(String(100), nullable=False, index=True)
    estado = Column(String(20), nullable=False)
    poliza = Column(String(100))
    monto = Column(Float)
    moneda = Column(String(3))
    proveedor_id = Column(String(100))
    fecha_actualizacion = Column(DateTime)
