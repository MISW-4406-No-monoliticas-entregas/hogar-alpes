"""Entidades y agregación raíz base."""
import uuid
from dataclasses import dataclass, field
from datetime import datetime

from seedwork.dominio.eventos import EventoDominio
from seedwork.dominio.mixins import ValidarReglasMixin


@dataclass
class Entidad:
    """Entidad con identidad propia (id) y trazabilidad temporal.

    La identidad, no los atributos, define la igualdad de una entidad.
    """
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    _fecha_creacion: datetime = field(default_factory=datetime.utcnow)
    _fecha_actualizacion: datetime = field(default_factory=datetime.utcnow)

    @property
    def fecha_creacion(self) -> datetime:
        return self._fecha_creacion

    @property
    def fecha_actualizacion(self) -> datetime:
        return self._fecha_actualizacion

    def _marcar_actualizacion(self):
        self._fecha_actualizacion = datetime.utcnow()

    def __eq__(self, other) -> bool:
        return isinstance(other, Entidad) and self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)


@dataclass
class AgregacionRaiz(Entidad, ValidarReglasMixin):
    """Raíz de un agregado.

    Decisión de diseño: el agregado ACUMULA eventos de dominio (agregar_evento)
    pero NO los publica. Publicar/despachar es responsabilidad de la Unidad de
    Trabajo tras confirmar la transacción. Así el dominio permanece libre de
    infraestructura (ítem 2, hexagonal) y las señales/Pulsar se disparan solo
    cuando el estado quedó persistido de forma consistente.
    """
    eventos: list[EventoDominio] = field(default_factory=list)

    def agregar_evento(self, evento: EventoDominio):
        self.eventos.append(evento)

    def limpiar_eventos(self):
        self.eventos = []
