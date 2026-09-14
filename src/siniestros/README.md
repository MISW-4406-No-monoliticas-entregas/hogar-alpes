# S2 — Trabajos Siniestros (Entrega 5: Event Sourcing)

Microservicio del dominio de siniestros. Desde esta entrega la persistencia del
agregado `Siniestro` es por **event sourcing**: la tabla `eventos_siniestro` es
la fuente de verdad; la tabla `estado_siniestro` es solo una proyección de
lectura reconstruible.

## Estado de las tareas de la entrega

| # | Tarea | Estado |
|---|-------|--------|
| 1 | Consumidor de comandos `Key_Shared` sobre `comandos.siniestros` (despacho por `type`, ack post-commit, nack en error, idempotencia por id de mensaje) | ✅ Completa y verificada end-to-end |
| 2 | Comandos nuevos `MarcarValidado` y `RechazarSiniestro` (+ eventos `SiniestroValidado` / `SiniestroRechazado` de dominio e integración) | ✅ Completa y verificada end-to-end |
| 3 | Event store (`eventos_siniestro`, repositorio con replay, versión incremental, conflicto de concurrencia optimista) | ✅ Completa; replay y conflicto cubiertos por tests (`tests/test_event_sourcing.py`) |
| 4 | Comando `ReconstruirProyeccion` (HTTP admin, total o por `id_siniestro`) | ✅ Completa y verificada (5 eventos reaplicados en la prueba) |
| 5 | Esquema v2 de `eventos.siniestros` con `canal_origen` (no activo) + test de compatibilidad | ✅ Completa (`schema/v2/eventos.py`, `tests/test_esquema_v2.py`) |

Los checkpoints 1 y 2 se corrieron contra `docker compose up` desde cero
(2026-09-14): levanta sin pasos manuales, el flujo comando → evento →
proyección → consulta funciona por el tópico, y matar el contenedor con un
comando pendiente no pierde el siniestro (Pulsar lo reentrega al reiniciar).

### Limitaciones conocidas / pendientes

- **Coordinación con S9 (ver sección al final)**: el esquema del comando cambió
  (ahora el sobre viaja de verdad); S9 debe actualizar su copia. Mientras tanto
  hay un puente de compatibilidad, pero es temporal.
- La tabla `siniestros` (CRUD de la E3) sigue existiendo y `RepositorioSiniestrosSQLAlchemy`
  se conserva como referencia, pero ya nada los escribe. Se pueden borrar cuando
  el equipo lo decida.
- El evento de dominio `SiniestroRegistrado` ahora incluye la dirección
  (`calle`, `ciudad`, `pais`): con event sourcing el evento es la única fuente
  de verdad y sin esos campos la dirección se perdería en el replay. El esquema
  de **integración** v1 no cambió (la dirección no viaja por el broker).

## Arquitectura del cambio

- **Entrada de producción**: el tópico `comandos.siniestros` (consumidor
  `Key_Shared`, suscripción `trabajos-siniestros-comandos`, despacho por el
  campo `type` del sobre). Los `POST` de la API HTTP quedan como **utilidades de
  prueba** para demos sin broker.
- **Escritura**: `RepositorioSiniestrosEventStore` implementa el mismo puerto
  `RepositorioSiniestros` del dominio. `agregar`/`actualizar` insertan solo los
  eventos nuevos con versión incremental por siniestro; el constraint único
  `(siniestro_id, version)` detecta escrituras concurrentes y lanza
  `ConflictoDeConcurrencia` (no se silencia: el consumidor hace nack y Pulsar
  reentrega).
- **Lectura del agregado**: `obtener_por_id` reconstruye el `Siniestro`
  reaplicando los eventos en orden con `Siniestro.aplicar(evento)` — replay sin
  revalidar reglas de negocio.
- **Idempotencia**: cada handler registra el id del mensaje en
  `mensajes_procesados` dentro de la MISMA transacción del negocio; el ack al
  broker se hace después del commit.
- **Consultas**: los `GET` leen SOLO de la proyección `estado_siniestro`,
  nunca del event store. La proyección y sus handlers de siempre no cambiaron
  (solo se agregaron handlers para los dos eventos nuevos).

## Cómo probar cada checkpoint

Todo se corre desde la raíz del repo. Primero:

```bash
docker compose up -d --build
```

### Checkpoint 1 — comando por el tópico crea el siniestro

```bash
docker compose exec siniestros python scripts/publicar_comando.py registrar
# tomar el siniestro_id de:
docker compose exec postgres-siniestros psql -U siniestros \
  -c "SELECT siniestro_id, tipo, version FROM eventos_siniestro;"
curl -s localhost:8000/siniestros/<id_siniestro>
```

### Checkpoint 2 — event store + resiliencia

```bash
# flujo completo por el tópico:
docker compose exec siniestros python scripts/publicar_comando.py asignar <id> prov-99
docker compose exec siniestros python scripts/publicar_comando.py validar <id>
# o rechazar en vez de validar:
docker compose exec siniestros python scripts/publicar_comando.py rechazar <id> poliza_vencida
curl -s localhost:8000/siniestros/<id>   # estado desde la proyección

# resiliencia: publicar con el proceso muerto y verificar que no se pierde
docker compose kill siniestros
docker compose run --rm --no-deps siniestros python scripts/publicar_comando.py registrar
docker compose start siniestros
# ~10s después el siniestro nuevo existe en eventos_siniestro y estado_siniestro
```

### Checkpoint 4 — reconstruir la proyección desde el event store

```bash
# sabotear la proyección a propósito:
docker compose exec postgres-siniestros psql -U siniestros -c "DELETE FROM estado_siniestro;"
# reconstruirla desde los eventos (total, o {"id_siniestro": "<id>"} para uno):
curl -s -X POST localhost:8000/admin/proyecciones/estado-siniestro/reconstruir
curl -s localhost:8000/siniestros/<id>   # vuelve a responder igual que antes
```

### Tests unitarios (replay, concurrencia, compatibilidad v1/v2)

Se corren fuera del contenedor (el `.dockerignore` excluye `tests/` de la
imagen a propósito):

```bash
cd src/siniestros && pip install -r requirements.txt && pytest -q
```

Nota: `pulsar-client==3.5.0` no tiene wheel para Python 3.13; con Python
local ≥3.13 instalar `pulsar-client>=3.6` y `fastavro>=1.10` solo para los
tests (la API usada es idéntica).

## ⚠️ Coordinación pendiente con S9 (esquema del comando)

**S2 es el dueño del esquema de `comandos.siniestros`.** En la E3 el sobre se
declaraba por herencia (`ComandoIntegracion(Mensaje)`), y por el bug documentado
en `docs/notas/nota-B-esquema-backward.md` (`pulsar.schema.Record` **no hereda**
campos de la clase base), `id`, `time`, `spec_version` y `type` **no viajaban**.
S9 copió ese esquema "tal cual" (así lo dice su propio código), o sea que hoy
S9 publica mensajes **sin sobre efectivo**: sin `type` no se puede despachar y
sin `id` no se puede deduplicar.

Esta entrega corrige el esquema del lado del dueño
(`modulos/siniestros/infraestructura/schema/v1/comandos.py`): sobre declarado en
la clase concreta + `data` con todos los campos opcionales (compatible BACKWARD
con lo publicado por S9, porque los campos nuevos son anulables).

**Lo que S9 tiene que hacer**: actualizar su copia del esquema
(`src/integraciones/.../schema/v1/comandos.py`) a esta forma exacta y llenar el
sobre (ya llena `id/time/type` en su despachador; solo le falta que el esquema
los declare). **Puente temporal**: mientras migra, los mensajes que lleguen con
`type` nulo se asumen `RegistrarSiniestro` con un warning ruidoso en el log y se
deduplican por el `message_id` del broker — funciona, pero no es el contrato.
Quitar ese puente (`_al_mensaje_sin_type` en
`modulos/siniestros/infraestructura/consumidores.py`) cuando S9 migre.
