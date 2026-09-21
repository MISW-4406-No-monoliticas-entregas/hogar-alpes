"""Modelo SQLAlchemy de la tabla `saga_log`.

Es el registro transversal de todo el proceso de negocio (registro +
validación + asignación), que hoy vive repartido entre S2/S10/S7 por diseño
de bounded contexts. No reemplaza el event store de S2 -- lo complementa a
nivel de proceso completo (ver README de este módulo).

`siniestro_id` es nullable porque la saga nace antes que el siniestro: S2 es
quien genera el id. Mientras tanto la fila se correlaciona por
(partner_id, poliza), y guarda servicio y zona, que no viajan en los eventos
de S2 y el paso de validacion necesita.
"""
from sqlalchemy import Column, String, DateTime

from config.db import Base


class SagaDTO(Base):
    __tablename__ = "saga_log"

    id = Column(String(36), primary_key=True)
    siniestro_id = Column(String(36), nullable=True, index=True)
    paso_actual = Column(String(20), nullable=False)
    estado = Column(String(20), nullable=False)
    proveedor_id = Column(String(36), nullable=True)
    motivo_fallo = Column(String(500), nullable=True)
    partner_id = Column(String(100), nullable=True, index=True)
    poliza = Column(String(100), nullable=True, index=True)
    servicio = Column(String(100), nullable=True)
    zona = Column(String(100), nullable=True)
    fecha_creacion = Column(DateTime, nullable=False)
    fecha_actualizacion = Column(DateTime, nullable=False)
