# S4 - Orquestador de sagas

Dirige la transaccion larga de atender un siniestro B2B2C y guarda en que paso
va cada una. Se reparte entre C (camino feliz) y D (compensacion y Saga Log),
en archivos separados: `aplicacion/comandos/pasos_felices.py` y
`aplicacion/comandos/compensaciones.py`.

Patron: **orquestacion**, no coreografia. Un solo servicio decide el orden de
los pasos y persiste el avance en una tabla, en vez de que cada servicio
reaccione a los eventos de los demas y haya que reconstruir el estado del
proceso correlacionando varios topicos.

## El flujo

```
POST /sagas
  -> RegistrarSiniestro   (comandos.siniestros)  PENDIENTE
S2: SiniestroRegistrado   (eventos.siniestros)   INICIADA
  -> ValidarSiniestro     (comandos.reglas)      VALIDANDO
S10: SiniestroAprobado... (eventos.reglas)
  -> MarcarValidado       (comandos.siniestros)
  -> AsignarProveedor     (comandos.matching)    ASIGNANDO
S7: ProveedorAsignado     (eventos.matching)     COMPLETADA
```

Camino de fallo, desde cualquier punto:

```
S10: SiniestroRechazadoPorReglas   -> COMPENSANDO -> COMPENSADA
S7:  SinProveedorDisponible        -> COMPENSANDO -> COMPENSADA
  compensaciones: RechazarSiniestro siempre, LiberarProveedor si habia reserva
```

Cuatro servicios participan: S2, S10, S7 y el propio S4.

## Por que la saga arranca en el orquestador

El paso de validacion necesita `servicio` y `zona`, y esos dos datos no viajan
en ningun evento de S2: no los recibe S9 del partner ni los guarda el agregado
Siniestro. Por eso el orquestador es quien recibe la peticion completa, guarda
servicio y zona en su fila, y publica el `RegistrarSiniestro`.

Como el id del siniestro lo genera S2, la saga nace en `PENDIENTE` sin
`siniestro_id` y se correlaciona despues por `(partner_id, poliza)` cuando
llega `SiniestroRegistrado`. Si no hay saga pendiente para ese par, el evento
se ignora: ese siniestro entro por otro camino (S9 directo) y no lo dirige el
orquestador.

**Limite conocido:** correlacionar por poliza funciona porque el par
(partner, poliza) identifica el reclamo, pero dos peticiones identicas
seguidas se atienden en orden de llegada. Lo correcto seria un
`correlation_id` propio del orquestador viajando en el sobre de
`comandos.siniestros`, que es un campo aditivo con default y por tanto
compatible hacia atras.

## Saga Log

Una fila por transaccion en la tabla `saga_log`, con el paso actual, el
estado, el proveedor reservado y el motivo del fallo. Es el registro
transversal del proceso completo, que hoy vive repartido entre tres bounded
contexts. Complementa el event store de S2, no lo reemplaza: alli se audita el
ciclo de vida del agregado Siniestro, aqui el de la transaccion.

Cada avance persiste antes de publicar el comando que sigue, y los pasos que
tienen dos fases (INICIADA/VALIDANDO y COMPENSANDO/COMPENSADA) usan dos
transacciones a proposito, para que una consulta en el punto intermedio vea el
paso de verdad.

## API

```
POST /sagas                  arranca la transaccion larga (202)
GET  /sagas/<id_siniestro>   estado de la saga de ese siniestro
GET  /sagas/por-id/<id_saga> estado por id de saga (util justo despues del POST)
GET  /sagas?limite=50        las ultimas sagas
GET  /salud
```

El BFF consume `GET /sagas/<id_siniestro>` desde `/siniestros/<id>/estado`.

## Correrlo

```bash
docker compose up -d --build
```

El servicio queda en el 8005. Una transaccion completa:

```bash
curl -s -X POST http://localhost:8005/sagas \
  -H 'Content-Type: application/json' \
  -d '{"partner_id":"seguros-alpes","poliza":"POL-1","monto":500000,
       "servicio":"plomeria","zona":"bogota-norte",
       "direccion":{"calle":"Cra 7","ciudad":"Bogota","pais":"CO"}}'

curl -s http://localhost:8005/sagas
```

Una que compensa, con un monto por encima del tope del partner:

```bash
curl -s -X POST http://localhost:8005/sagas \
  -H 'Content-Type: application/json' \
  -d '{"partner_id":"banco-andes","poliza":"POL-2","monto":5000000,
       "servicio":"plomeria","zona":"bogota-norte",
       "direccion":{"calle":"Cra 7","ciudad":"Bogota","pais":"CO"}}'
```

El Saga Log por SQL:

```bash
docker compose exec postgres-orquestador psql -U orquestador -d orquestador \
  -c "SELECT siniestro_id, paso_actual, estado, motivo_fallo FROM saga_log;"
```

## Pruebas

```bash
cd src/orquestador && pip install -r requirements.txt && pytest -v
```

26 pruebas sobre SQLite real y un despachador espia en vez de Pulsar:
`test_saga.py` y `test_pasos_felices.py` para el dominio y los comandos de
cada camino, `test_repositorio_sagas.py` para el repositorio y la consulta SQL
directa, y `test_compensaciones.py` para la compensacion completa.

## Limite conocido

El commit y la publicacion del comando que sigue son dos pasos separados. Si
el proceso muere entre los dos, la fila queda en el paso anterior y la saga se
detiene. Se ve en la tabla, pero no se recupera sola. La solucion es el patron
outbox: escribir el comando saliente en la misma transaccion del agregado y
que un relay lo publique.
