"""Modelo SQLAlchemy de la tabla `saga_log`.

Es el registro transversal de todo el proceso de negocio (registro +
validación + asignación), que hoy vive repartido entre S2/S10/S7 por diseño
de bounded contexts. No reemplaza el event store de S2 -- lo complementa a
nivel de proceso completo (ver README de este módulo).
"""
from sqlalchemy import Column, String, DateTime

from config.db import Base


class SagaDTO(Base):
    __tablename__ = "saga_log"

    id = Column(String(36), primary_key=True)
    siniestro_id = Column(String(36), nullable=False, index=True)
    paso_actual = Column(String(20), nullable=False)
    estado = Column(String(20), nullable=False)
    proveedor_id = Column(String(36), nullable=True)
    motivo_fallo = Column(String(500), nullable=True)
    fecha_creacion = Column(DateTime, nullable=False)
    fecha_actualizacion = Column(DateTime, nullable=False)
