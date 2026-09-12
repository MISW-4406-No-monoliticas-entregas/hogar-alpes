"""Eventos de dominio del módulo ejemplo."""
import uuid
from dataclasses import dataclass

from seedwork.dominio.eventos import EventoDominio


@dataclass
class EjemploCreado(EventoDominio):
    id_ejemplo: uuid.UUID = None
    nombre: str = None
    estado: str = None
