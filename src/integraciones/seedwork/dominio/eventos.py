"""Eventos de dominio base."""
import uuid
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class EventoDominio:
    """Evento de dominio base."""
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    fecha_evento: datetime = field(default_factory=datetime.utcnow)
