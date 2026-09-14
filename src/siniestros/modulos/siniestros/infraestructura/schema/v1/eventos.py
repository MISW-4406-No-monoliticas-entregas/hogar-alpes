"""Esquema Avro v1 del tópico eventos.siniestros (sobre único por tópico).

Un solo esquema por tópico + namespace en BACKWARD => el registry rechaza un
cambio incompatible (escenario 6 demostrable). El tipo concreto va en `type`;
`data` lleva todos los campos posibles, opcionales con default.

Los campos del sobre van declarados aquí y no por herencia (pulsar.schema no
hereda campos de la clase base; ver docs/notas/nota-B-esquema-backward.md).
"""
from pulsar.schema import Record, String, Float, Long


class DatosSiniestro(Record):
    # Todos opcionales con default => un solo esquema sirve para todos los
    # tipos de evento del tópico, y añadir un campo nuevo es backward-compatible.
    id_siniestro = String(required=False, default="")
    partner_id = String(required=False, default="")
    poliza = String(required=False, default="")
    monto = Float(required=False, default=0.0)
    moneda = String(required=False, default="")
    proveedor_id = String(required=False, default="")
    estado = String(required=False, default="")
    motivo = String(required=False, default="")


class EventoSiniestros(Record):
    # Campos del sobre declarados AQUÍ (pulsar.schema no hereda de la base).
    id = String()
    time = Long()
    spec_version = String()
    # "SiniestroRegistrado" | "ProveedorAsignado" | "SiniestroValidado" | "SiniestroRechazado"
    type = String()
    data = DatosSiniestro()
