"""Esquema Avro v1 del tópico eventos.matching (sobre único por tópico).

`type` distingue ProveedorAsignado de SinProveedorDisponible. Llevan los datos
relevantes del agregado (no solo el id): no hay llamados síncronos para que un
consumidor pregunte por el resto.
"""
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
    # Campos del sobre declarados aquí porque pulsar.schema NO hereda de la base.
    id = String()
    time = Long()
    spec_version = String()
    type = String()  # "ProveedorAsignado" | "SinProveedorDisponible"
    data = DatosEventoMatching()
