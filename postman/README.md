# Colección Postman — Flujo E2E (S9 → S2 → S10 → S7)

Recorre la transacción larga completa de la Entrega 4 contra el `docker
compose up` local: S9 registra el siniestro de un partner, S2 lo persiste
(event store + proyección), S10 lo valida contra el contrato del partner y S7
reserva un proveedor.

> Para la arquitectura completa (los 4 servicios, tópicos, esquemas) ver el
> [README raíz](../README.md). Este documento es solo sobre cómo correr la
> colección y el script de demo.

## Por qué hay dos piezas (colección + script)

Postman y Newman solo hablan **HTTP**. Los pasos 3 y 4 de la rúbrica piden
publicar **a mano** en los tópicos reales (`comandos.reglas`,
`comandos.matching`) — eso es Pulsar, no HTTP, y ningún servicio expone un
atajo HTTP equivalente para S7 (a propósito: S7 no tiene un endpoint de
comandos, solo consultas GET).

Por eso:

- **`hogar-alpes-e2e.postman_collection.json`** trae todos los requests HTTP
  (POST a S9, GETs de verificación en S2/S10/S7) para explorar el flujo a
  mano en la UI de Postman. Las carpetas 3 y 4 traen en su `description` el
  comando exacto para publicar el tópico real antes de correr esos GET.
- **`demo.py`** hace **todo** de punta a punta en un solo comando: los pasos
  HTTP con `urllib` (sin dependencias) y los dos pasos de tópico invocando
  `docker compose exec` sobre las herramientas que ya trae cada servicio
  (`tools/publicar_comando.py` en S10, `scripts/publicar_prueba.py` en S7) —
  así no se reimplementan sus esquemas Avro aquí, y cada servicio sigue
  siendo dueño del suyo.

## Requisitos

- El stack levantado: `docker compose up --build` desde la raíz del repo,
  con los cuatro servicios (`integraciones`, `siniestros`, `reglas`,
  `matching`) corriendo.
- Python 3.8+ para `demo.py` (solo librería estándar, no hace falta
  `pip install` nada).
- Postman (o Newman) solo si quieres correr la colección directamente; no es
  necesario para `demo.py`.

## Correr todo de punta a punta (recomendado)

```bash
python postman/demo.py
```

Corre dos casos completos y termina con un resumen:

1. **Con cobertura de proveedor** — servicio `plomeria`, zona `bogota-norte`:
   S9 registra → S2 proyecta → S10 aprueba (seguros-alpes cubre plomería en
   bogotá-norte) → S7 encuentra proveedor disponible y publica
   `ProveedorAsignado`.
2. **Sin cobertura de proveedor** — servicio `carpinteria`, zona
   `bogota-norte`: mismo camino por S9/S2/S10 (seguros-alpes también cubre
   carpintería ahí, así que **igual queda aprobado por reglas**), pero S7 no
   tiene ningún carpintero disponible en esa zona y publica
   `SinProveedorDisponible`. Así se ve que la falta de cobertura es un
   problema de **S7**, no de la validación de S10.

El script es **repetible**: la semilla de S7 solo trae un proveedor
disponible de plomería en bogotá-norte, así que al final del caso 1, si quedó
`ASIGNADA`, el script publica `LiberarProveedor` para dejarlo libre de nuevo
(igual que haría la saga de la E5 al compensar). Sin este paso, correr
`demo.py` una segunda vez ya no encontraría cobertura.

Salida esperada (resumida):

```
- Con cobertura de proveedor (plomeria / bogota-norte)
    póliza        : POL-DEMO-COBERTURA-1234567890
    id_siniestro  : 3f2a...
    S10 (reglas)  : APROBADO
    S7 (matching) : ASIGNADA (Plomería Los Alpes)

- Sin cobertura de proveedor (carpinteria / bogota-norte)
    póliza        : POL-DEMO-SINCOBERTURA-1234567890
    id_siniestro  : 9c1e...
    S10 (reglas)  : APROBADO
    S7 (matching) : SIN_PROVEEDOR (sin proveedor)
```

Código de salida `0` si ambos casos llegaron a buen término, `1` si algo
falló (por ejemplo, si algún servicio no está arriba).

## Correr la colección a mano en Postman

1. Importa `hogar-alpes-e2e.postman_collection.json` en Postman.
2. Corre la carpeta **"1. S9 - Registrar siniestro"** completa (genera una
   póliza única por corrida con un pre-request script).
3. Corre **"2. S2 - Verificar registro"**: el primer request busca el
   siniestro por número de póliza (S9 no conoce el `id_siniestro` en esta
   entrega parcial, no hay saga todavía) y guarda `idSiniestroConCobertura`
   / `idSiniestroSinCobertura` como variables de colección. Si el test dice
   "todavía no está", el consumo es asíncrono — espera un segundo y vuelve a
   correr ese mismo request.
4. Antes de correr **"3. S10 - Validar siniestro"**, publica el comando real
   (el `description` de la carpeta trae el comando exacto, con las variables
   ya resueltas):
   ```bash
   docker compose exec reglas python tools/publicar_comando.py <id_siniestro> seguros-alpes <monto> <servicio> <zona>
   ```
   Luego corre los GET de la carpeta.
5. Antes de correr **"4. S7 - Asignar proveedor"**, publica el comando real:
   ```bash
   docker compose exec matching python scripts/publicar_prueba.py asignar <id_siniestro> <servicio> <zona>
   ```
   Luego corre los GET de la carpeta.

## Variables de la colección

| Variable | Uso |
|---|---|
| `s9`, `s2`, `s10`, `s7` | Base URLs (puertos del compose local: 8001/8000/8002/8003) |
| `partnerId` | `seguros-alpes` (partner con traductor y contrato de reglas ya sembrados) |
| `servicioConCobertura` / `zonaConCobertura` | `plomeria` / `bogota-norte` — S7 sí tiene proveedor disponible |
| `servicioSinCobertura` / `zonaSinCobertura` | `carpinteria` / `bogota-norte` — S7 no tiene proveedor disponible |
| `polizaConCobertura` / `polizaSinCobertura` | Generadas por pre-request script (únicas por corrida) |
| `idSiniestroConCobertura` / `idSiniestroSinCobertura` | Capturadas en el paso 2, se reusan en 3 y 4 |

## Nota sobre el esquema de `eventos.siniestros`

Si al correr esto ves errores `IncompatibleSchema` en los logs de `siniestros`
o `reglas`, es porque algún consumidor se suscribió a `eventos.siniestros`
antes de que S2 publicara nada y Pulsar registró un esquema incompatible con
el de S2. Se soluciona reseteando el esquema del tópico (estado del broker,
no de código):

```bash
docker compose exec pulsar bin/pulsar-admin schemas delete \
  persistent://hogar-alpes/siniestros-b2b2c/eventos.siniestros
```

y reiniciando los servicios que lo consumen/producen (`siniestros`, `reglas`,
`matching`).
