# Nota para B (S2 - Trabajos Siniestros) — migración a namespace nuevo + BACKWARD

Contexto: en la Entrega 4 movimos la topología de Pulsar a
`persistent://hogar-alpes/siniestros-b2b2c/*` y pusimos el **namespace en
`BACKWARD`** para poder demostrar la validación del registry en el escenario 6
(evolución retrocompatible de esquema).

Hay **dos cambios** que te tocan. El primero ya está aplicado (solo config); el
segundo lo dejamos pendiente para ti porque toca tu código de dominio/infra.

---

## 1) Rename de tópico (YA aplicado, solo configuración)

En el `docker-compose.yml` de la raíz el servicio `siniestros` ahora recibe:

```
TOPICO_EVENTOS  = persistent://hogar-alpes/siniestros-b2b2c/eventos.siniestros
TOPICO_COMANDOS = persistent://hogar-alpes/siniestros-b2b2c/comandos.siniestros
```

(antes: `eventos.trabajos` y `comandos.siniestros` en `public/default`).

No cambia código: `config/settings.py` ya lee esas variables. Solo revisa que
sigas leyéndolas por entorno.

**Además:** `api/__init__.py` sigue llamando
`configurar_namespace_multiesquema(PULSAR_ADMIN_URL)`, que fija `public/default`
en `ALWAYS_COMPATIBLE`. Con el namespace nuevo eso quedó como código muerto
(apunta a un namespace que ya no usamos). La topología del namespace real la fija
ahora `infra/pulsar/crear_topicos.sh` vía el servicio `pulsar-init`. Puedes
**borrar** esa llamada de `create_app` cuando confirmes que todo levanta.

---

## 2) Sobre Avro único por tópico (PENDIENTE — lo aplicas tú)

**Por qué:** hoy `eventos.siniestros` transporta **dos** esquemas Avro distintos
(`EventoSiniestroRegistrado` y `EventoProveedorAsignado`). Con el namespace en
`BACKWARD`, el broker acepta el **primer** esquema que llegue y **rechaza** el
segundo (no son compatibles entre sí). Resultado:

- `POST /siniestros`  → publica `SiniestroRegistrado` → **OK** (primer esquema).
- `POST /siniestros/<id>/proveedor` → publica `ProveedorAsignado` → **falla** al
  registrar el segundo esquema en el mismo tópico.

**Solución (opción b acordada):** un **sobre único** por tópico con discriminador
`type` y un `data` que contiene todos los campos posibles, todos **opcionales con
default**. Así hay un solo esquema por tópico y `BACKWARD` sí protege (rechaza
quitar un campo o cambiar un tipo sin default = escenario 6 demostrable).

Es un cambio **aditivo en 2 archivos**. `handlers.py` y los tests **no cambian**
(conservo las firmas de los métodos del despachador).

> ⚠️ **Bug latente que encontré al verificar la plantilla:** `pulsar.schema.Record`
> **NO hereda los campos de la clase base** (su metaclase solo lee el namespace de
> la clase concreta). Hoy `EventoIntegracion(Mensaje)` con solo `data` genera un
> esquema Avro que **pierde** `id`, `time`, `spec_version` y `type`: se serializan
> como null y al consumir `sobre.type` devuelve el descriptor, no el valor. En la
> E3 no se notó porque nadie consumía del broker. Por eso, en el refactor de abajo,
> los 4 campos del sobre van **declarados directamente en `EventoSiniestros`**, no
> heredados. (Lo mismo aplica a `ComandoRegistrarSiniestro`: si algún consumidor va
> a despachar por `type`, hay que declararle los campos del sobre.)

### `modulos/siniestros/infraestructura/schema/v1/eventos.py`

```python
"""Esquema Avro v1: un sobre único por tópico para eventos.siniestros."""
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


class EventoSiniestros(Record):
    # Campos del sobre declarados AQUÍ (pulsar.schema no hereda de la base).
    id = String()
    time = Long()
    spec_version = String()
    type = String()  # "SiniestroRegistrado" | "ProveedorAsignado"
    data = DatosSiniestro()
```

### `modulos/siniestros/infraestructura/despachadores.py`

```python
"""Despachador de eventos de integración a Pulsar."""
from seedwork.infraestructura.pulsar import Despachador
from seedwork.infraestructura.utils import tiempo_actual_ms, generar_uuid
from config.settings import PULSAR_URL, TOPICO_EVENTOS
from modulos.siniestros.dominio.eventos import SiniestroRegistrado, ProveedorAsignado
from modulos.siniestros.infraestructura.schema.v1.eventos import (
    EventoSiniestros,
    DatosSiniestro,
)


class DespachadorEventos(Despachador):
    def __init__(self, url_broker: str = PULSAR_URL):
        super().__init__(url_broker)

    def publicar_evento(self, evento, topico: str):
        raise NotImplementedError

    def publicar_siniestro_registrado(self, evento: SiniestroRegistrado):
        mensaje = EventoSiniestros(
            id=generar_uuid(), time=tiempo_actual_ms(), spec_version="v1",
            type="SiniestroRegistrado",
            data=DatosSiniestro(
                id_siniestro=str(evento.id_siniestro),
                partner_id=evento.partner_id,
                poliza=evento.poliza,
                monto=evento.monto,
                moneda=evento.moneda,
                estado=evento.estado,
            ),
        )
        self._publicar_mensaje(mensaje, TOPICO_EVENTOS, EventoSiniestros)

    def publicar_proveedor_asignado(self, evento: ProveedorAsignado):
        mensaje = EventoSiniestros(
            id=generar_uuid(), time=tiempo_actual_ms(), spec_version="v1",
            type="ProveedorAsignado",
            data=DatosSiniestro(
                id_siniestro=str(evento.id_siniestro),
                proveedor_id=evento.proveedor_id,
                estado=evento.estado,
            ),
        )
        self._publicar_mensaje(mensaje, TOPICO_EVENTOS, EventoSiniestros)
```

Un consumidor del tópico despacha por `mensaje.value().type`. En la plantilla
(`src/_plantilla/`) dejamos ese patrón (sobre único + despacho por `type` +
`Key_Shared` + ack tardío + idempotencia) listo para copiar.
