# BFF — interfaz síncrona hacia afuera (Entrega 5)

Backend for Frontend del POC **Hogar de los Alpes**. Expone una API REST en
español para que sistemas externos (o un futuro frontend) usen las capacidades
de negocio por llamados **síncronos**. Es la **única pieza del sistema
autorizada a hacerle HTTP a los demás servicios**; entre ellos, S9/S2/S10/S7 y
el orquestador siguen comunicándose solo por comandos y eventos en Pulsar.

> Para la arquitectura completa (los 4 servicios, tópicos, esquemas y
> despliegue) ver el [README raíz](../../README.md).

## Qué es y qué no es

- **Es un adaptador delgado.** Traduce cada ruta HTTP del BFF en **una** llamada
  HTTP a **un** servicio y devuelve su respuesta tal cual (sin reinterpretarla).
  No reimplementa lógica de negocio de ningún dominio.
- **No tiene base de datos ni cliente de Pulsar.** El registro de siniestros
  pasa por S9 (que es quien publica el comando `RegistrarSiniestro` en
  `comandos.siniestros`); el BFF **no publica comandos** él mismo.
- **No arma el estado de la transacción larga combinando servicios.** Esa foto
  consolidada es el Saga Log del orquestador (S4); el BFF solo se la pide.
- **No inventa contratos.** Cada ruta del BFF apunta a una ruta que existe hoy
  en el servicio destino (verificadas leyendo su código). La única excepción
  es el orquestador, que todavía no existe en este repo: su contrato esperado
  está documentado abajo y el cliente queda listo para consumirlo.

## Endpoints: a quién le pega cada uno

| Método | Ruta del BFF | Servicio al que llama | Ruta real en el servicio | Estado |
|---|---|---|---|---|
| `POST` | `/siniestros` | **S9 Integraciones** | `POST /partners/<partner_id>/siniestros` | ✅ completo |
| `GET` | `/sincronizaciones/<id>` | S9 Integraciones | `GET /sincronizaciones/<id>` | ✅ completo |
| `GET` | `/siniestros/<id>` | **S2 Siniestros** | `GET /siniestros/<id>` (proyección) | ✅ completo |
| `GET` | `/partners/<partner_id>/siniestros` | S2 Siniestros | `GET /partners/<partner_id>/siniestros` | ✅ completo |
| `GET` | `/siniestros/<id>/estado` | **S4 Orquestador** (Saga Log) | `GET /sagas/<id_siniestro>` *(contrato esperado)* | ⏳ depende de la rama del orquestador |
| `GET` | `/siniestros/<id>/asignacion` | S7 Matching | `GET /asignaciones/<id_siniestro>` | ✅ completo |
| `GET` | `/reglas/<partner_id>` | **S10 Reglas** | `GET /partners/<partner_id>/reglas` | ✅ completo |
| `GET` | `/reglas/<partner_id>/validaciones?limite=` | S10 Reglas | `GET /partners/<partner_id>/validaciones?limite=` | ✅ completo |
| `GET` | `/proveedores?zona=&servicio=` | **S7 Matching** | `GET /proveedores?zona=&servicio=` | ✅ completo |
| `GET` | `/salud` | — (el propio BFF) | — | ✅ completo |
| `GET` | `/salud/dependencias` | S9, S2, S10, S7, S4 (`/salud` de cada uno) | diagnóstico de infraestructura, no de negocio | ✅ completo |

Por qué cada destino (regla central del BFF):

- **Registrar** → S9. Es el ACL de entrada; el registro sigue el flujo normal
  (S9 publica el comando, el resto reacciona por eventos). El BFF no le habla
  al orquestador para esto.
- **"¿En qué va este siniestro?"** (paso actual, completada, compensada) → el
  orquestador, sobre su Saga Log. No se reconstruye combinando S2+S10+S7.
- **Detalle del agregado** (monto, póliza, estado, proveedor) → S2 directo.
- **Reglas / historial de validaciones de un partner** → S10 directo.
- **Proveedores por zona/servicio**, **asignación** de un siniestro → S7 directo.

### Qué está completo y qué depende de otra rama

- **Completo y verificado contra `docker compose up`** (2026-09-17): todos los
  endpoints hacia S9, S2, S10 y S7, la salud y todos los casos de error de la
  tabla de abajo (409 de S9, 404 de S2/S10/S7, 400 de validación, 503 con un
  servicio apagado). Un `POST /siniestros` al BFF dejó el comando en
  `comandos.siniestros`, S2 lo consumió y el siniestro quedó en
  `eventos_siniestro` y en la proyección (`GET /siniestros/<id>` → `REGISTRADO`).
- **Depende de la rama del orquestador (S4):** `GET /siniestros/<id>/estado`.
  El orquestador **no existe todavía en ninguna rama de este repositorio**
  (se revisó `src/` y todas las ramas remotas). Mientras `ORQUESTADOR_URL`
  esté vacía el BFF responde **501** con un mensaje explícito; en cuanto el
  servicio exista basta con definir la variable (hay una línea comentada en
  el `docker-compose.yml`). Ver "Contrato esperado del orquestador".
- **Limitación heredada del flujo actual (no del BFF):** `POST /siniestros`
  devuelve el `id_sincronizacion` de S9, **no** el `id_siniestro` (lo asigna
  S2 al consumir el comando y S9 no lo conoce todavía; `id_siniestro` viene
  `null` en `GET /sincronizaciones/<id>`). Para ubicar el siniestro recién
  registrado se usa `GET /partners/<partner_id>/siniestros` y se busca por
  póliza (así lo hace también la colección Postman). Cuando la saga
  correlacione el id de vuelta en S9, este mismo endpoint lo devolverá sin
  cambios en el BFF.

## Contrato esperado del orquestador (S4)

El cliente `clientes/cliente_orquestador.py` consume:

```
GET {ORQUESTADOR_URL}/sagas/<id_siniestro>

200 {
  "id_siniestro": "…",
  "paso_actual":  "RegistrarSiniestro" | "ValidarSiniestro" | "AsignarProveedor",
  "estado":       "EN_PROGRESO" | "COMPLETADA" | "COMPENSADA" | "FALLIDA",
  "historial": [
    {"paso": "RegistrarSiniestro", "estado": "OK", "fecha": "…", "detalle": "…"},
    …
  ]
}
404 si no hay saga para ese siniestro.
```

El BFF lo devuelve **tal cual** en `GET /siniestros/<id>/estado`. Si el equipo
del orquestador define otra ruta o forma, el único cambio es la ruta en
`obtener_saga`; nada más del BFF depende de la forma del cuerpo. Falta
confirmar con ese equipo que el Saga Log se consulte por `id_siniestro` (y no
por un id de saga distinto); si fuera por id de saga, haría falta además que
S9 o el orquestador devuelvan esa correlación al registrar.

## Cuerpo de `POST /siniestros`

```json
{
  "partner_id": "seguros-alpes",
  "siniestro": { …payload en el formato PROPIO del partner… }
}
```

`siniestro` se reenvía **sin tocar** a `POST /partners/<partner_id>/siniestros`
de S9: la traducción al modelo canónico es responsabilidad del ACL (S9), no del
BFF. Los formatos vigentes están en
`src/integraciones/modulos/sincronizaciones/aplicacion/traductores/`:

- `seguros-alpes`: `numeroReclamo`, `poliza`, `montoEstimado`, `moneda`,
  `direccion: {calle, ciudad, pais}`.
- `banco-andes`: `ref`, `policy_number`, `amount: {value, currency}`,
  `address` ("calle, ciudad, pais").

Respuesta: la de S9 sin cambios (`202 {id_sincronizacion, estado: "PUBLICADA"}`,
`409` si ese `partner_id + id externo` ya se recibió, `400` partner o payload
inválido).

## Manejo de errores

Toda respuesta de error es JSON `{"error", "servicio", "detalle"?}`. Si un
servicio no responde, el BFF devuelve un error claro, no se cuelga (timeouts
de conexión y lectura configurables).

| Situación | Código del BFF |
|---|---|
| Cuerpo o parámetros inválidos (validación del propio BFF) | `400` |
| El servicio respondió `4xx` (`400`, `404`, `409`…) | **el mismo `4xx`**, con `servicio` y `detalle` |
| El servicio respondió `5xx` | `502` |
| El servicio no está integrado en este despliegue (orquestador sin URL) | `501` |
| No se pudo conectar con el servicio (caído) | `503` |
| El servicio no respondió dentro del timeout | `504` |

## Estructura

```
src/bff/
├── main.py                  punto de entrada (solo Flask; sin consumidores ni BD)
├── api/                     adaptador HTTP de entrada
│   ├── __init__.py          create_app()
│   ├── errores.py           traducción de errores de clientes -> códigos HTTP
│   ├── siniestros.py        POST /siniestros (S9), GET detalle (S2), estado (S4), asignación (S7)
│   ├── reglas.py            GET /reglas/… (S10)
│   ├── proveedores.py       GET /proveedores (S7)
│   └── salud.py             /salud, /salud/dependencias
├── clientes/                un cliente HTTP por servicio (adaptadores de salida)
│   ├── base.py              sesión, timeouts, traducción de errores de red
│   ├── errores.py           ServicioNoConfigurado / NoDisponible / TiempoAgotado / RespuestaErronea
│   ├── cliente_s9.py        S9 Integraciones
│   ├── cliente_s2.py        S2 Siniestros
│   ├── cliente_s10.py       S10 Reglas
│   ├── cliente_s7.py        S7 Matching
│   └── cliente_orquestador.py  S4 (contrato esperado)
├── config/settings.py       URLs y timeouts por variable de entorno
├── tests/                   pruebas unitarias (clientes con sesión simulada, rutas con dobles)
├── postman/hogar-alpes-bff.postman_collection.json
├── Dockerfile · requirements.txt · pytest.ini
```

## Configuración (variables de entorno)

| Variable | Default (fuera de Docker) | En el compose | Descripción |
|---|---|---|---|
| `INTEGRACIONES_URL` | `http://localhost:8001` | `http://integraciones:5000` | S9 |
| `SINIESTROS_URL` | `http://localhost:8000` | `http://siniestros:5000` | S2 |
| `REGLAS_URL` | `http://localhost:8002` | `http://reglas:5000` | S10 |
| `MATCHING_URL` | `http://localhost:8003` | `http://matching:5000` | S7 |
| `ORQUESTADOR_URL` | *(vacía)* | *(comentada)* | S4. Vacía = no integrado → `501` en `/siniestros/<id>/estado` |
| `TIMEOUT_CONEXION_SEGUNDOS` | `2` | `2` | Timeout para abrir conexión |
| `TIMEOUT_LECTURA_SEGUNDOS` | `5` | `5` | Timeout esperando respuesta |
| `PORT` | `5000` | `5000` (publicado en `8004`) | Puerto HTTP |

## Cómo levantarlo

Con todo el stack, desde la raíz del repo (el BFF ya está en el
`docker-compose.yml` y en el `docker-compose.cluster.yml`; no hay pasos manuales):

```bash
docker compose up --build
# BFF en http://localhost:8004
```

Solo el BFF (y sus dependencias) sobre un stack ya levantado:

```bash
docker compose up -d --build bff
```

Fuera de Docker, contra el compose local (usa los defaults de `settings.py`):

```bash
cd src/bff && pip install -r requirements.txt && python main.py
```

## Pruebas

```bash
cd src/bff && pip install -r requirements.txt && pytest -q
```

No necesitan ningún servicio arriba: los clientes se prueban con una sesión
`requests` simulada (timeouts, conexión rechazada, `4xx`/`5xx`, URL vacía) y
las rutas con el cliente de pruebas de Flask y los clientes reemplazados por
dobles (cada ruta llama al servicio correcto con los argumentos correctos y
cada error se traduce al código documentado).

## Colección Postman

`postman/hogar-alpes-bff.postman_collection.json`: **todos** los endpoints del
BFF (solo del BFF, no de los servicios internos), listos para importar. Usa la
variable de colección `{{bff_url}}` (por defecto `http://localhost:8004`);
cámbiala para apuntar a GCP. Las carpetas siguen el orden del flujo: salud →
registrar (S9) → detalle (S2) → estado de la transacción (S4) → reglas (S10) →
proveedores (S7). El request de registro genera una póliza única por corrida y
el de listado captura el `idSiniestro` para los siguientes.

## Probar cada endpoint a mano (curl)

```bash
BFF=http://localhost:8004

# Salud del BFF y de sus dependencias
curl -s $BFF/salud
curl -s $BFF/salud/dependencias

# 1. Registrar un siniestro (-> S9). Mismo efecto que un POST directo a S9:
#    nuevo comando RegistrarSiniestro en comandos.siniestros.
curl -s -X POST $BFF/siniestros -H 'Content-Type: application/json' -d '{
  "partner_id": "seguros-alpes",
  "siniestro": {
    "numeroReclamo": "SA-1001", "poliza": "POL-123", "montoEstimado": 500000, "moneda": "COP",
    "direccion": {"calle": "Cra 7 # 1-2", "ciudad": "Bogota", "pais": "CO"}
  }}'
# -> 202 {"id_sincronizacion": "...", "estado": "PUBLICADA"}   (409 si se repite)

#    Otro partner, otro formato (la traducción la hace S9):
curl -s -X POST $BFF/siniestros -H 'Content-Type: application/json' -d '{
  "partner_id": "banco-andes",
  "siniestro": {"ref": "BA-778", "policy_number": "POL-12",
                "amount": {"value": 1200000, "currency": "COP"},
                "address": "Calle 1 # 2-3, Bogota, CO"}}'

#    Confirmar que S9 lo publicó (-> S9)
curl -s $BFF/sincronizaciones/<id_sincronizacion>

# 2. Ubicar el siniestro por póliza y ver su detalle (-> S2, proyección)
curl -s $BFF/partners/seguros-alpes/siniestros
curl -s $BFF/siniestros/<id_siniestro>
# -> {"estado": "REGISTRADO", "poliza": "POL-123", "monto": 500000.0, ...}

# 3. Estado de la transacción larga (-> orquestador S4, Saga Log)
curl -s $BFF/siniestros/<id_siniestro>/estado
# -> 501 mientras ORQUESTADOR_URL esté vacía; con S4 integrado:
#    {"paso_actual": "...", "estado": "EN_PROGRESO|COMPLETADA|COMPENSADA", "historial": [...]}

# 4. Reglas e historial de validaciones de un partner (-> S10)
curl -s $BFF/reglas/seguros-alpes
curl -s "$BFF/reglas/seguros-alpes/validaciones?limite=10"

# 5. Proveedores por zona y servicio, y asignación de un siniestro (-> S7)
curl -s "$BFF/proveedores?zona=bogota-norte&servicio=plomeria"
curl -s $BFF/siniestros/<id_siniestro>/asignacion
# -> 404 hasta que se publique AsignarProveedor para ese siniestro

# Errores claros (nunca se cuelga)
curl -s $BFF/siniestros/no-existe            # 404 {"error": "...", "servicio": "S2 Siniestros"}
curl -s "$BFF/proveedores"                    # 400 faltan zona/servicio
docker compose stop matching && curl -s "$BFF/proveedores?zona=bogota-norte&servicio=plomeria"
# -> 503 {"error": "S7 Matching no está disponible: no se pudo conectar", ...}
docker compose start matching
```

Para verificar que el `POST /siniestros` del BFF dejó el comando en el tópico
y S2 lo consumió:

```bash
docker compose exec postgres-siniestros psql -U siniestros \
  -c "select siniestro_id, tipo, version from eventos_siniestro order by fecha desc limit 3;"
```
