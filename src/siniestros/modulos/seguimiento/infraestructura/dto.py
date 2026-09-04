"""Modelo SQLAlchemy de la proyección (tabla `estado_siniestro`).

Tabla de lectura separada de `siniestros` (CQRS): la escritura y la lectura no
comparten tabla, lo que permite escalarlas y optimizarlas por separado
(atributo de calidad: escalabilidad, Entrega 4).
"""
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
