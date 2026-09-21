"""Convención del sobre de mensajes Avro (v1).

IMPORTANTE: `pulsar.schema.Record` NO hereda los campos de una clase base
(su metaclase solo lee el namespace de la clase concreta). Por eso los campos
del sobre se declaran DIRECTAMENTE en cada Record concreto (ComandoEjemplo,
EventoEjemplo), no por herencia. Esta clase queda como documentación del
contrato del sobre; no la uses como base de un esquema Avro.

Sobre estándar (mismos nombres en todos los tópicos):
    id            String   id único del mensaje (idempotencia del consumidor)
    time          Long     epoch en milisegundos
    spec_version  String   versión del esquema ("v1", "v2", ...)
    type          String   tipo concreto para despachar ("CrearEjemplo", ...)
    data          Record   carga con todos los campos posibles, opcionales
"""
from pulsar.schema import Record, String, Long


class Mensaje(Record):
    id = String()
    time = Long()
    spec_version = String()
    type = String()
