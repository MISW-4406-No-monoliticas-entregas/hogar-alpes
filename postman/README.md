# Colección Postman unificada — Saga completa (S4) + BFF

Recorre la transacción larga completa de la Entrega 5 contra el `docker
compose up` local: arranca la saga en el orquestador (S4), la deja correr
sola por comandos/eventos en Pulsar (registro en S2, validación en S10,
asignación en S7, o compensación si algo falla), y hace el seguimiento a
través del BFF, la única puerta síncrona hacia afuera.

> Para la arquitectura completa (los 5+1 servicios, tópicos, esquemas) ver el
> [README raíz](../README.md). Este documento es solo sobre cómo correr la
> colección y el script de demo.

## Qué cambió desde la Entrega 4

En la E4, `comandos.reglas` y `comandos.matching` se publicaban **a mano**
(Postman no habla Pulsar, así que había que invocar un script por fuera para
cada paso). Ahora que existe `POST /sagas` en el orquestador (S4), **todo el
flujo es HTTP puro**: un solo POST arranca la transacción larga completa y el
resto avanza solo. La colección y `demo.py` de esta carpeta ya no necesitan
tocar Pulsar directamente en ningún punto del camino feliz ni del de fallo.

## Por qué hay dos piezas (colección + script)

- **`hogar-alpes-e2e.postman_collection.json`** — para explorar el flujo a
  mano en la UI de Postman, carpeta por carpeta, con asserts en cada paso.
- **`demo.py`** — corre **todo** de punta a punta en un solo comando, sin
  dependencias externas (`urllib` de la librería estándar), con polling
  automático hasta que la saga llega a un paso terminal.

Ambas piezas cubren los mismos dos casos: **con cobertura de proveedor**
(termina `COMPLETADA`) y **sin cobertura** (termina `COMPENSADA`).

## Requisitos

- El stack levantado: `docker compose up --build` desde la raíz del repo
  (los 6 servicios: `integraciones`, `siniestros`, `reglas`, `matching`,
  `orquestador`, `bff`).
- Python 3.8+ para `demo.py` (solo librería estándar).
- Postman (o Newman) solo si quieres correr la colección directamente.

## Correr todo de punta a punta (recomendado)

```bash
python postman/demo.py
```

Corre dos casos completos y termina con un resumen:

1. **Con cobertura de proveedor** — servicio `plomeria`, zona `bogota-norte`:
   `POST /sagas` arranca la saga → S2 registra → S10 aprueba (seguros-alpes
   cubre plomería en bogotá-norte) → S7 encuentra proveedor disponible → la
   saga queda `COMPLETADA`.
2. **Sin cobertura de proveedor** — servicio `carpinteria`, zona
   `bogota-norte`: mismo camino por S2/S10 (seguros-alpes también cubre
   carpintería ahí, así que **igual queda aprobado por reglas**), pero S7 no
   tiene ningún carpintero disponible → la saga se compensa sola
   (`RechazarSiniestro` a S2) y queda `COMPENSADA`. Así se ve que la falta de
   cobertura es un problema de **S7**, no de la validación de S10.

El script es **repetible**: la semilla de S7 solo trae un proveedor
disponible de plomería en bogotá-norte, así que al final del caso 1 el script
libera ese proveedor (vía `scripts/publicar_prueba.py liberar` de S7) para
poder volver a correr `demo.py` las veces que haga falta. Es una limpieza de
conveniencia del script de demo, no algo que haga la saga real: una
`COMPLETADA` de verdad se queda así.

Salida esperada (resumida):

```
- Con cobertura de proveedor (plomeria / bogota-norte)
    póliza        : POL-DEMO-COBERTURA-1234567890
    id_saga       : 48ba09f2-...
    id_siniestro  : d1689745-...
    paso_actual   : COMPLETADA (saga OK)
    proveedor     : 63c41149-...

- Sin cobertura de proveedor (carpinteria / bogota-norte)
    póliza        : POL-DEMO-SINCOBERTURA-1234567890
    id_saga       : 13b3e927-...
    id_siniestro  : ced928e1-...
    paso_actual   : COMPENSADA (saga FALLIDO)
    motivo_fallo  : Sin proveedor disponible para el servicio/zona solicitados
```

Código de salida `0` si ambos casos llegaron a un paso terminal, `1` si algo
falló (por ejemplo, si algún servicio no está arriba).

## Correr la colección a mano en Postman (o con Newman)

Toda la colección corre en un solo `newman run` sin pasos manuales de por
medio (confirmado: 16/16 requests, 23/23 asserts, 0 fallos):

```bash
npx newman run postman/hogar-alpes-e2e.postman_collection.json --delay-request 800
```

El `--delay-request` le da tiempo a la saga (1-3 s) para llegar a un paso
terminal antes de que la carpeta 2 la consulte. Corriendo a mano en la UI de
Postman no hace falta el delay: basta con esperar un segundo entre la
carpeta 1 y la 2.

Carpetas:

1. **Iniciar la transacción larga (S4 Orquestador)** — `POST /sagas` para
   los dos casos; genera una póliza única por corrida.
2. **Seguimiento de la saga** — `GET /sagas/por-id/:id` directo al
   orquestador, y el mismo dato a través de `GET /siniestros/:id/estado` del
   BFF (prueba que el BFF es una puerta real, no una copia).
3. **Vista unificada del siniestro (vía BFF)** — detalle (S2), asignación
   (S7), validaciones (S10) y proveedores (S7), todo a través del BFF.
4. **Registro directo sin saga (legado, vía BFF)** — `POST /siniestros` del
   BFF sigue reenviando a S9 tal cual la E4; no arranca una saga.
5. **Consultas directas a cada servicio (depuración, sin BFF)** — las mismas
   vistas del paso 3 pero sin pasar por el BFF, para aislar fallas.

> Nota de repetibilidad: a diferencia de `demo.py`, la colección **no**
> libera el proveedor al final (Postman no habla Pulsar). Si corres la
> colección varias veces seguidas sin correr `demo.py` de por medio, el caso
> "con cobertura" puede terminar `COMPENSADA` por agotar el único proveedor
> de la semilla — no es un bug, es la semilla agotándose. Corre `demo.py` una
> vez para liberarlo, o reinicia el stack (`docker compose down -v && up`).

## Variables de la colección

| Variable | Uso |
|---|---|
| `orquestador`, `bff`, `s2`, `s10`, `s7` | Base URLs (puertos del compose local: 8005/8004/8000/8002/8003) |
| `partnerId` | `seguros-alpes` (partner con traductor y contrato de reglas ya sembrados) |
| `servicioConCobertura` / `zonaConCobertura` | `plomeria` / `bogota-norte` — S7 sí tiene proveedor disponible |
| `servicioSinCobertura` / `zonaSinCobertura` | `carpinteria` / `bogota-norte` — S7 no tiene proveedor disponible |
| `polizaConCobertura` / `polizaSinCobertura` | Generadas por pre-request script (únicas por corrida) |
| `idSagaConCobertura` / `idSagaSinCobertura` | Capturadas al iniciar la saga (paso 1) |
| `idSiniestroConCobertura` / `idSiniestroSinCobertura` | Capturadas al consultar la saga (paso 2), se reusan en 3 y 5 |

## Nota sobre el esquema de `eventos.siniestros`

Si al correr esto ves errores `IncompatibleSchema` en los logs de
`siniestros`, `reglas`, `matching` u `orquestador`, es porque algún
consumidor se suscribió a `eventos.siniestros` antes de que S2 publicara nada
y Pulsar registró un esquema incompatible. Se soluciona reseteando el
esquema del tópico (estado del broker, no de código):

```bash
docker compose exec pulsar bin/pulsar-admin schemas delete \
  persistent://hogar-alpes/siniestros-b2b2c/eventos.siniestros
```

y reiniciando los servicios que lo consumen/producen.
