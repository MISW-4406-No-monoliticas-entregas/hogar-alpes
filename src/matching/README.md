# S7 — Matching de Proveedores

Microservicio dueño del agregado `Asignacion` y del modelo de lectura/config
`ProveedorHabilitado`. Busca y reserva un proveedor acreditado para atender un
siniestro ya aprobado. Recibe comandos por el tópico `comandos.matching`,
reserva (o no) un proveedor y publica el resultado en `eventos.matching`.

> Este README describe el servicio de forma aislada. Para la arquitectura
> completa del POC (los 4 servicios, tópicos, esquemas y despliegue) ver el
> [README raíz](../../README.md).

## Modelo de dominio

- **Agregado raíz:** `Asignacion` (siniestro, servicio, zona, proveedor
  asignado, estado, fechas). Es **CRUD**, no Event Sourcing.
- **Modelo de lectura/config:** `ProveedorHabilitado` — una fila por
  (proveedor, servicio, zona) con su disponibilidad. Se siembra al arrancar
  (ver `modulos/matching/infraestructura/semilla.py`) para poder demostrar
  tanto la asignación exitosa como el caso sin cobertura.
- **Objetos valor:** `Servicio`, `Zona`.
- **Comandos:** `AsignarProveedor`, `LiberarProveedor` (compensación).
- **Eventos de dominio → integración:** `ProveedorAsignado`,
  `SinProveedorDisponible`. Llevan los datos relevantes del agregado, no solo
  el id (no hay llamados síncronos para que un consumidor pregunte por el
  resto).
- **Reglas de negocio:** el siniestro es obligatorio; solo se puede liberar
  una asignación que esté en estado `ASIGNADA`.

## Flujo de comandos

- **`AsignarProveedor`** (`id_siniestro`, `servicio`, `zona`): busca un
  `ProveedorHabilitado` disponible para ese servicio/zona.
  - Si lo encuentra: lo marca `disponible=False`, crea la `Asignacion` en
    estado `ASIGNADA` y publica `ProveedorAsignado`.
  - Si no: crea la `Asignacion` en estado `SIN_PROVEEDOR` y publica
    `SinProveedorDisponible`.
- **`LiberarProveedor`** (`id_siniestro`, `proveedor_id`): compensación que
  una saga futura usará para deshacer una asignación (hoy se invoca a mano).
  Marca la asignación como `LIBERADA` y el proveedor como disponible de
  nuevo. **No publica evento** todavía: no está en el contrato de esta
  entrega y la orquestación completa es de una entrega futura.

## Suscripción de solo-log a `eventos.siniestros`

S7 también se suscribe a `eventos.siniestros` (S2), pero **sin lógica de
negocio todavía**: solo registra en log lo que recibe
(`modulos/matching/infraestructura/consumidor_eventos_siniestros.py`). Es
intencional en esta entrega parcial — demuestra que los servicios ya se oyen
entre sí, aunque la orquestación completa (saga) venga después. El esquema
consumido es una **copia propia** (`schema/v1/eventos_siniestros.py`) del que
publica S2; no se importa código entre servicios.

## Decisiones de diseño

- **Arquitectura hexagonal.** El dominio no depende de Flask, SQLAlchemy ni
  del cliente de Pulsar; la API y los consumidores del broker son adaptadores
  de entrada, el repositorio y el despachador son adaptadores de salida.
- **Patrón de consumidor de la plantilla.** `ConsumidorBase` con suscripción
  `Key_Shared`, `ack` **después** del commit de la Unidad de Trabajo,
  `negative_acknowledge` en error, e idempotencia por `id` de mensaje
  (tabla `mensajes_procesados`, registrada en la misma transacción que el
  negocio).
- **`ProveedorHabilitado` no es agregación raíz.** No tiene invariantes de
  negocio propias ni emite eventos; es el modelo de lectura/config que
  alimenta el matching. Su disponibilidad se muta como efecto colateral de
  manejar comandos sobre `Asignacion`, dentro de la misma transacción.

## Configuración (variables de entorno)

| Variable | Default | Descripción |
|---|---|---|
| `DB_HOST` / `DB_PORT` | `localhost` / `5432` | PostgreSQL |
| `DB_USER` / `DB_PASSWORD` / `DB_NAME` | `matching` | Credenciales de desarrollo |
| `PULSAR_URL` | `pulsar://localhost:6650` | Broker |
| `TOPICO_COMANDOS` | `…/comandos.matching` | Comandos por broker (entrada) |
| `TOPICO_EVENTOS` | `…/eventos.matching` | Eventos de integración (salida) |
| `TOPICO_EVENTOS_SINIESTROS` | `…/eventos.siniestros` | Tópico de S2 al que S7 solo loguea |
| `CONSUMIR_COMANDOS` | `true` | Arranca el consumidor de `comandos.matching` |
| `CONSUMIR_EVENTOS_SINIESTROS` | `true` | Arranca el suscriptor de solo-log a `eventos.siniestros` |

## API

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/proveedores?zona=<zona>&servicio=<servicio>` | Proveedores habilitados por zona y servicio |
| `GET` | `/asignaciones/<id_siniestro>` | Estado de la asignación de un siniestro (proveedor reservado, o `SIN_PROVEEDOR`) |
| `GET` | `/salud` | Verificación de disponibilidad |

## Pruebas

```bash
cd src/matching && pip install -r requirements.txt && pytest
```

Cubre las reglas de negocio del agregado `Asignacion`: asignación exitosa,
`SinProveedorDisponible`, invariantes de liberación y de siniestro obligatorio.

## Probar el flujo manualmente

Ver la sección "Probar S7 manualmente" del [README raíz](../../README.md#probar-s7-matching-manualmente).
