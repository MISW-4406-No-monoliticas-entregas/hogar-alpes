"""Copia (lado consumidor) del esquema Avro v1 de eventos.siniestros (S2).

Copia FIEL del esquema del dueno: mismo nombre de record y mismos campos. Un
set de campos distinto rompe la resolucion Avro y, bajo BACKWARD, bloquea al
productor de S2 en el cluster (IncompatibleSchema).
"""
from pulsar.schema import Record, String, Long, Float


class DatosSiniestro(Record):
    id_siniestro = String(required=False, default="")
    partner_id = String(required=False, default="")
    poliza = String(required=False, default="")
    monto = Float(required=False, default=0.0)
    moneda = String(required=False, default="")
    proveedor_id = String(required=False, default="")
    estado = String(required=False, default="")
    motivo = String(required=False, default="")


class EventoSiniestros(Record):
    id = String()
    time = Long()
    spec_version = String()
    type = String()
    data = DatosSiniestro()
