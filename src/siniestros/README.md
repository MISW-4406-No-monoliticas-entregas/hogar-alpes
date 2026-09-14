# S2 — Trabajos Siniestros

Microservicio dueño del agregado `Siniestro` y de su ciclo de vida. Es el núcleo
de la línea B2B2C (70 % del volumen). Recibe comandos por el tópico
`comandos.siniestros`, aplica las invariantes del dominio, persiste el estado y
publica eventos en `eventos.siniestros`.

> Este README describe el servicio de forma aislada. Para la arquitectura
> completa del POC (los 4 servicios, tópicos, esquemas y despliegue) ver el
> [README raíz](../../README.md).

## Arquitectura interna

Dos módulos que no se conocen entre sí y se comunican por eventos de dominio:

- **`siniestros`** — lado de escritura. Agregado `Siniestro` y lógica de negocio.
- **`seguimiento`** — lado de lectura (CQRS). Proyección `estado_siniestro`
  optimizada para consulta, que reacciona a los eventos de `siniestros`.

Cada evento de dominio se despacha de dos maneras:

1. **En proceso**, por el mediador de señales del `seedwork`, para actualizar la
   proyección de `seguimiento`.
2. **Hacia el broker**, traducido a evento de integración Avro en
   `eventos.siniestros`, para el resto de la plataforma.

## Modelo de dominio

- **Agregado raíz:** `Siniestro`, con entidades hijas `Evidencia` y `Actividad`.
- **Objetos valor:** `Direccion`, `Monto`, `EstadoSiniestro`, `Poliza`, `PartnerId`.
- **Comandos:** `RegistrarSiniestro`, `AsignarProveedor` (+ `MarcarValidado`,
  `RechazarSiniestro` en la evolución de la E4).
- **Eventos de dominio:** `SiniestroRegistrado`, `ProveedorAsignado`.
- **Reglas de negocio** (invariantes del agregado):
  - la póliza es obligatoria,
  - el monto estimado debe ser positivo,
  - un siniestro solo puede asignarse a un proveedor si está en estado registrado.

## Decisiones de diseño

- **Arquitectura hexagonal.** El dominio no depende de infraestructura ni del
  framework web; las dependencias apuntan hacia el dominio. La API y el consumidor
  del broker son adaptadores de entrada; el repositorio y el despachador son
  adaptadores de salida.
- **CQRS.** Escritura (`siniestros`) y lectura (`seguimiento`) tienen modelos,
  tablas y rutas de código distintas y escalan de forma independiente.
- **La Unidad de Trabajo es la única que publica eventos.** El agregado acumula
  sus eventos pero no los emite; la UoW los despacha tras confirmar la
  transacción, de modo que nada se publica si la persistencia falla.
- **Fábrica del agregado.** Aplica las invariantes en la construcción.
- **Esquemas Avro versionados (`schema/v1/`).** La evolución retrocompatible
  (campos con default en `v2`) cambia el contrato sin romper consumidores.

## Configuración (variables de entorno)

| Variable | Default | Descripción |
|---|---|---|
| `DB_HOST` / `DB_PORT` | `localhost` / `5432` | PostgreSQL |
| `DB_USER` / `DB_PASSWORD` / `DB_NAME` | `siniestros` | Credenciales de desarrollo |
| `PULSAR_URL` | `pulsar://localhost:6650` | Broker |
| `TOPICO_COMANDOS` | `…/comandos.siniestros` | Comandos por broker (entrada) |
| `TOPICO_EVENTOS` | `…/eventos.siniestros` | Eventos de integración (salida) |
| `CONSUMIR_COMANDOS` | `true` | Arranca el consumidor de comandos |

## API

| Método | Ruta | Descripción |
|---|---|---|
| `GET`  | `/siniestros/<id>` | Estado de un siniestro (proyección) |
| `GET`  | `/partners/<id>/siniestros` | Siniestros de un partner (proyección) |
| `GET`  | `/salud` | Verificación de disponibilidad |
| `POST` | `/siniestros` | Registro por HTTP — **utilidad de prueba**; la entrada entre servicios es `comandos.siniestros` |

## Pruebas

```bash
cd src/siniestros && pip install -r requirements.txt && pytest
```

Cubre las reglas de negocio del agregado y el flujo comando → evento de dominio →
proyección → consulta.
