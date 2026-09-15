"""Serialización de eventos de dominio hacia/desde el event store (JSON).

El payload guardado en `eventos_siniestro.datos` es el dataclass del evento de
dominio con los tipos no-JSON (UUID, datetime) convertidos a texto. Al leer, se
reconstruye la clase concreta a partir de la columna `tipo`.
"""
import dataclasses
import uuid
from datetime import datetime

from seedwork.dominio.eventos import EventoDominio
from modulos.siniestros.dominio.eventos import (
    SiniestroRegistrado,
    ProveedorAsignado,
    SiniestroValidado,
    SiniestroRechazado,
)

_TIPOS: dict[str, type[EventoDominio]] = {
    clase.__name__: clase
    for clase in (
        SiniestroRegistrado,
        ProveedorAsignado,
        SiniestroValidado,
        SiniestroRechazado,
    )
}


def _a_json(valor):
    if isinstance(valor, uuid.UUID):
        return str(valor)
    if isinstance(valor, datetime):
        return valor.isoformat()
    return valor


def evento_a_dict(evento: EventoDominio) -> dict:
    return {
        campo.name: _a_json(getattr(evento, campo.name))
        for campo in dataclasses.fields(evento)
    }


def dict_a_evento(tipo: str, datos: dict) -> EventoDominio:
    clase = _TIPOS.get(tipo)
    if clase is None:
        raise ValueError(f"Tipo de evento desconocido en el event store: '{tipo}'")
    datos = dict(datos)
    if "id" in datos:
        datos["id"] = uuid.UUID(datos["id"])
    if "fecha_evento" in datos:
        datos["fecha_evento"] = datetime.fromisoformat(datos["fecha_evento"])
    nombres = {campo.name for campo in dataclasses.fields(clase)}
    # Se ignoran llaves que la clase ya no tenga (eventos viejos con más campos).
    return clase(**{k: v for k, v in datos.items() if k in nombres})
