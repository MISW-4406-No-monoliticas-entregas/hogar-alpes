"""Copia del esquema del topico eventos.siniestros, cuyo dueno es S2.

Ningun servicio importa codigo de otro: el consumidor copia el contrato del
productor en su propio schema/v1. Si S2 cambia el sobre, avisa y se actualiza
esta copia.
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
