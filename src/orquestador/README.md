# S4 — Orquestador (slice de D: compensación + Saga Log)

Este directorio es el servicio **S4 Orquestador** de la Entrega 5, compartido
entre **C** (camino feliz: `RegistrarSiniestro → ValidarSiniestro →
AsignarProveedor`) y **D** (camino de fallo: compensación + Saga Log). Viven
en la misma rama (`feat/s4-orquestador`) pero en archivos separados para
minimizar conflictos de merge.

> **Este commit trae solo la parte de D.** No hay `Dockerfile`, `main.py`,
> `api/` ni entrada en `docker-compose.yml` todavía — se decidió a propósito
> para poder construir y probar el Saga Log + la compensación de forma
> aislada, sin bloquear el trabajo en C. Ensamblar el servicio completo
> (arrancar los consumidores desde un `main.py`, exponer los `GET` de
> consulta, Dockerfile, y la entrada en `docker-compose.yml`) es el siguiente
> paso, una vez el camino feliz de C esté integrado.

## Qué hay aquí (D)

- **`modulos/orquestador/dominio/entidades.py`** — agregado `Saga` (el Saga
  Log). **Archivo compartido con C**: trae los métodos de compensación
  (`iniciar`, `registrar_proveedor_reservado`, `compensar`,
  `completar_compensacion`) documentados para que C agregue los del camino
  feliz sin chocar. Avisar antes de tocarlo.
- **`modulos/orquestador/aplicacion/comandos/compensaciones.py`** — los dos
  comandos de D: `RegistrarProveedorAsignado` (bookkeeping cuando S7
  confirma una reserva) y `CompensarSaga` (el camino de fallo completo).
  El contraparte de C es `pasos_felices.py`, en el mismo directorio.
- **`modulos/orquestador/infraestructura/`** — persistencia del Saga Log
  (`saga_log`, tabla propia en la BD de S4), despachador de las
  compensaciones (`RechazarSiniestro` a `comandos.siniestros`,
  `LiberarProveedor` a `comandos.matching`), y los consumidores reales de
  `eventos.reglas` y `eventos.matching`.

## Cómo decide la compensación ("según corresponda")

`CompensarSaga` siempre publica `RechazarSiniestro` (el siniestro no se
puede completar). Además publica `LiberarProveedor` **solo si** la saga ya
tenía un `proveedor_id` anotado (`RegistrarProveedorAsignado` lo registra
cuando llega `ProveedorAsignado` de S7). En el flujo de 3 pasos de esta
entrega, ninguno de los dos disparadores reales (`SiniestroRechazadoPorReglas`,
`SinProveedorDisponible`) deja un proveedor reservado —by diseño, esos
eventos significan justamente que no se llegó a reservar nada—, así que en
la práctica solo se ve `RechazarSiniestro`. El mecanismo general para
liberar sí está implementado y probado
(`test_compensar_con_proveedor_reservado_tambien_libera`), listo para
cuando la saga tenga un paso posterior a la asignación que pueda fallar.

## Máquina de estados de la saga

```
INICIADA → VALIDANDO → ASIGNANDO → COMPLETADA        (camino feliz, C)
                                 ↘
                                  COMPENSANDO → COMPENSADA   (camino de fallo, D)
```

`CompensarSaga` persiste el paso en **dos transacciones separadas**
(COMPENSANDO primero, COMPENSADA después) para que una consulta SQL en el
punto intermedio muestre de verdad `COMPENSANDO` — no es un detalle
cosmético, es el criterio de aceptación de esta pieza.

## Por qué existe el Saga Log (para la sustentación)

El event store de S2 audita correctamente el ciclo de vida del agregado
`Siniestro`, pero el historial completo del proceso de negocio (registro +
validación + asignación) está repartido entre tres bounded contexts
distintos (S2, S10, S7) por diseño — cada uno solo ve su pedazo. El Saga Log
es el registro transversal que faltaba: **complementa** el event store de
S2, no lo reemplaza ni lo contamina con eventos que no son del agregado
`Siniestro`.

## Demo con SQL (sin servicio corriendo todavía)

Sin Postgres en este slice, la demostración corre contra SQLite en memoria
en los tests (SQL real, no un doble):

```bash
cd src/orquestador && pip install -r requirements.txt && pytest -v
```

`tests/test_repositorio_sagas.py::test_consulta_sql_directa_a_la_tabla_saga_log`
ejercita literalmente el criterio de aceptación: compensa una saga y hace un
`SELECT paso_actual, estado, motivo_fallo FROM saga_log WHERE siniestro_id = :sid`
directo, sin pasar por el repositorio.

Cuando el servicio esté ensamblado con Postgres real, la misma consulta se
corre así:

```bash
docker compose exec postgres-orquestador psql -U orquestador -d orquestador \
  -c "SELECT siniestro_id, paso_actual, estado, motivo_fallo FROM saga_log;"
```

## Pruebas

```bash
cd src/orquestador && pip install -r requirements.txt && pytest -v
```

14 pruebas:
- `test_saga.py` — dominio aislado (sin BD ni Pulsar): la máquina de
  estados, la invariante de que solo se compensa una saga `EN_CURSO`, y que
  la compensación incluye o no `proveedor_id` según corresponda.
- `test_repositorio_sagas.py` — el repositorio contra SQLite real, incluida
  la consulta SQL directa del criterio de aceptación.
- `test_compensaciones.py` — integración de los comandos completos (Unidad
  de Trabajo + repositorio + despachador de prueba en vez de Pulsar real):
  idempotencia por `id_mensaje`, "según corresponda", y las dos fases
  COMPENSANDO→COMPENSADA verificadas contra la fila persistida.

## Pendiente para ensamblar el servicio completo

- [ ] `pasos_felices.py` de C (motor de orquestación del camino feliz).
- [ ] Métodos del camino feliz en `dominio/entidades.py` (avanzar de paso,
      completar) — coordinarlos con C antes de tocar el archivo.
- [ ] `main.py` que arranque los 2+ consumidores (los de D ya están listos:
      `suscribirse_a_eventos_reglas`, `suscribirse_a_eventos_matching`).
- [ ] `api/` con el `GET` de consulta del Saga Log (`vistas.obtener_por_siniestro`
      y la query `ObtenerSagaPorSiniestro` ya existen, solo falta el blueprint).
- [ ] `Dockerfile`, `.dockerignore`, `postgres-orquestador` y la entrada
      `orquestador` en el `docker-compose.yml` raíz.
- [ ] Tópicos `comandos.orquestador`/`eventos.orquestador` si el diseño final
      del camino feliz los necesita (no los usa la parte de D).
