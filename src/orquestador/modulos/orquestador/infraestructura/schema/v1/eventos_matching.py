"""Copia (lado consumidor) del esquema Avro v1 de eventos.matching (S7)."""
from pulsar.schema import Record, String, Long


class DatosEventoMatching(Record):
    id_asignacion = String(required=False, default="")
    id_siniestro = String(required=False, default="")
    proveedor_id = String(required=False, default="")
    nombre_proveedor = String(required=False, default="")
    servicio = String(required=False, default="")
    zona = String(required=False, default="")
    estado = String(required=False, default="")


class EventoMatching(Record):
    id = String()
    time = Long()
    spec_version = String()
    type = String()  # D consume "SinProveedorDisponible" y "ProveedorAsignado"
    data = DatosEventoMatching()
