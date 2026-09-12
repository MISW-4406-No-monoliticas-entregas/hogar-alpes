"""Esquema Avro v1 del tópico eventos.ejemplo (sobre único por tópico)."""
from pulsar.schema import Record, String, Long


class DatosEventoEjemplo(Record):
    id_ejemplo = String(required=False, default="")
    nombre = String(required=False, default="")
    estado = String(required=False, default="")


class EventoEjemplo(Record):
    # Campos del sobre declarados aquí porque pulsar.schema NO hereda de la base.
    id = String()
    time = Long()
    spec_version = String()
    type = String()  # "EjemploCreado"
    data = DatosEventoEjemplo()
