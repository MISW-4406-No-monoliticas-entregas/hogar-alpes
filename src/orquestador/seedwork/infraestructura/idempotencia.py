"""Idempotencia del consumidor: no procesar dos veces el mismo mensaje.

Tabla `mensajes_procesados` con el id del mensaje del broker como PK. El registro
del id se hace DENTRO de la misma transacción (UoW) que el trabajo de negocio, de
modo que "procesado" y "efecto de negocio" se confirman juntos o no se confirman.
Si el mensaje se reentrega (p. ej. porque cayó una réplica antes del ack), el
INSERT choca con la PK y sabemos que ya se procesó. Responde al escenario 7.
"""
from sqlalchemy import Column, String, BigInteger
from sqlalchemy.exc import IntegrityError

from config.db import Base
from seedwork.infraestructura.utils import tiempo_actual_ms


class MensajeProcesado(Base):
    __tablename__ = "mensajes_procesados"
    id_mensaje = Column(String, primary_key=True)
    procesado_en = Column(BigInteger, nullable=False)


class MensajeDuplicado(Exception):
    """El mensaje ya había sido procesado."""


def registrar_mensaje(session, id_mensaje: str) -> None:
    """Marca el mensaje como procesado en la sesión actual.

    Lanza MensajeDuplicado si ya existía (el llamador hace rollback y ack).
    """
    session.add(MensajeProcesado(id_mensaje=id_mensaje, procesado_en=tiempo_actual_ms()))
    try:
        session.flush()  # fuerza el INSERT para detectar el choque de PK ya
    except IntegrityError as exc:
        session.rollback()
        raise MensajeDuplicado(id_mensaje) from exc
