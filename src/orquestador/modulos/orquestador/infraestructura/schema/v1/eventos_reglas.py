"""Copia (lado consumidor) del esquema Avro v1 de eventos.reglas (S10)."""
from pulsar.schema import Record, String, Long, Float


class DatosEventoReglas(Record):
    id_validacion = String(required=False, default="")
    id_siniestro = String(required=False, default="")
    partner_id = String(required=False, default="")
    monto = Float(required=False, default=0.0)
    moneda = String(required=False, default="COP")
    servicio = String(required=False, default="")
    zona = String(required=False, default="")
    resultado = String(required=False, default="")
    motivo = String(required=False, default="")


class EventoReglas(Record):
    id = String()
    time = Long()
    spec_version = String()
    type = String()  # D consume "SiniestroRechazadoPorReglas"
    data = DatosEventoReglas()
