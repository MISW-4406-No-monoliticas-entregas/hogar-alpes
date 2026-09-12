"""Esquema Avro v1 del tópico comandos.ejemplo (sobre único por tópico).

Un solo esquema por tópico + namespace en BACKWARD => el registry rechaza un
cambio incompatible. El tipo concreto va en `type`; `data` lleva todos los
campos posibles, opcionales con default (así añadir un campo es aditivo).
"""
from pulsar.schema import Record, String, Long


class DatosComandoEjemplo(Record):
    id_ejemplo = String(required=False, default="")
    nombre = String(required=False, default="")


class ComandoEjemplo(Record):
    # Campos del sobre declarados aquí porque pulsar.schema NO hereda de la base.
    # Ver seedwork/infraestructura/schema/v1/mensajes.py (convención del sobre).
    id = String()
    time = Long()
    spec_version = String()
    type = String()  # "CrearEjemplo" (agrega más tipos a medida que crezca el tópico)
    data = DatosComandoEjemplo()
