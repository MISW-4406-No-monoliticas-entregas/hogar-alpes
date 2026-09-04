"""Eventos de dominio base."""
import uuid
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class EventoDominio:
    """Base de todos los eventos de dominio (nombrados en participio pasado).

    Los agregados los acumulan; la Unidad de Trabajo los despacha al confirmar.
    El dominio nunca publica directamente en el broker (ítem 2: hexagonal).
    """
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    fecha_evento: datetime = field(default_factory=datetime.utcnow)
