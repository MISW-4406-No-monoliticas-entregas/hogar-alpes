"""Esquema Avro v1 del topico comandos.reglas (sobre unico por topico).

Un solo esquema por topico mas el namespace en BACKWARD hacen que el registry
rechace un cambio incompatible. El tipo concreto viaja en `type` y `data` lleva
todos los campos posibles, opcionales con default, para que agregar un campo sea
un cambio aditivo.
"""
from pulsar.schema import Record, String, Long, Float


class DatosComandoReglas(Record):
    id_siniestro = String(required=False, default="")
    partner_id = String(required=False, default="")
    monto = Float(required=False, default=0.0)
    moneda = String(required=False, default="COP")
    servicio = String(required=False, default="")
    zona = String(required=False, default="")


class ComandoReglas(Record):
    id = String()
    time = Long()
    spec_version = String()
    type = String()
    data = DatosComandoReglas()
