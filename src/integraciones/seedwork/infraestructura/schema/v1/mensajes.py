"""Esquemas base de mensajes Avro (v1).

Nota (pulsar.schema): un Record NO hereda los campos de su clase base; solo se
serializan los campos declarados en la clase concreta. Por eso:

- `ComandoIntegracion`/`EventoIntegracion` con subclases que solo declaran `data`
  producen un esquema con únicamente `data` (los campos de `Mensaje` NO viajan).
  Se conservan así A PROPÓSITO para copiar el esquema del comando RegistrarSiniestro
  EXACTAMENTE como lo tiene el servicio Siniestros (interoperabilidad del comando:
  el dueño del esquema es quien lo consume).
- Cuando S9 es dueño del tópico (eventos.partners) y quiere que `type` viaje para
  despachar por tipo, declara los campos del sobre EN LA CLASE CONCRETA del esquema
  (ver modulos/sincronizaciones/infraestructura/schema/v1/eventos.py).
"""
from pulsar.schema import Record, String, Long


class Mensaje(Record):
    id = String()
    time = Long()
    spec_version = String()
    type = String()


class EventoIntegracion(Mensaje):
    ...


class ComandoIntegracion(Mensaje):
    ...
