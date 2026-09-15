# S10 Reglas de Partner

Decide si un siniestro cumple lo pactado con el partner que lo envia. Es el
servicio que en la Entrega 2 se llamaba de forma sincrona desde Trabajos
Siniestros y que ahora solo se comunica por comandos y eventos.

## Que hace

- Consume `comandos.reglas` y ejecuta `ValidarSiniestro`.
- Evalua el siniestro contra el contrato del partner y guarda la validacion.
- Publica `SiniestroAprobadoPorReglas` o `SiniestroRechazadoPorReglas` en `eventos.reglas`.
- Se suscribe a `eventos.siniestros` y por ahora solo registra en log lo que emite S2.
  Esa suscripcion es la que demuestra que los servicios se oyen entre si en esta
  entrega parcial. En la Entrega 5 la saga es la que reacciona.
- Expone dos consultas GET.

## Dominio

`ReglaDePartner` es el agregado que guarda lo pactado: monto maximo cubierto,
servicios cubiertos y zonas habilitadas. Su metodo `evaluar` aplica esas
condiciones y devuelve un veredicto sin mutar nada ni emitir eventos.

`Validacion` es el agregado que registra el veredicto de una evaluacion sobre un
siniestro concreto. Es quien emite el evento de dominio, porque es el unico que
sabe si el resultado fue aprobado o rechazado.

La separacion es deliberada: la politica y el registro de su aplicacion tienen
ciclos de vida distintos. La regla de un partner cambia pocas veces al ano, las
validaciones se crean con cada siniestro.

Un siniestro se rechaza cuando el contrato esta inactivo, cuando la moneda no es
la pactada, cuando el monto supera el maximo, cuando el servicio no esta cubierto
o cuando la zona no esta habilitada. Si el partner no tiene contrato cargado
tambien se rechaza, y queda registrado el motivo.

## Datos

Modelo CRUD con dos tablas en su propia base PostgreSQL, `reglas_partner` y
`validaciones`, mas la tabla `mensajes_procesados` del seedwork. Ningun otro
servicio lee esta base: la topologia es descentralizada.

CRUD y no Event Sourcing porque una regla de partner es configuracion y una
validacion es un registro sin transiciones de estado. No hay historia que
reconstruir, asi que Event Sourcing seria complejidad sin beneficio.

## Esquemas

Un sobre Avro unico por topico con discriminador `type` y un `data` de campos
opcionales con default. El namespace esta en BACKWARD, de modo que el registry
rechaza un cambio incompatible y agregar un campo nuevo sigue siendo valido.

El contrato de `eventos.siniestros` es de S2. Este servicio lo copia en
`schema/v1/eventos_siniestros.py` en vez de importar codigo de S2, porque ningun
servicio importa a otro.

## Escenarios de calidad que sostiene

El consumidor usa suscripcion `Key_Shared` con el id del siniestro como llave,
confirma el mensaje solo despues del commit de la Unidad de Trabajo y registra el
id del mensaje en esa misma transaccion. Con eso, perder una replica no pierde ni
duplica validaciones, que es el escenario de disponibilidad.

Que la validacion ya no sea una llamada sincrona es lo que hace que la ingesta de
siniestros no se frene si este servicio se cae. Se gana disponibilidad a costa de
latencia en el camino critico.

## Limite conocido

El evento de integracion se publica despues del commit de la Unidad de Trabajo.
Si el proceso muere entre el commit y la publicacion, el evento se pierde: es el
problema del dual-write. La solucion es el patron outbox, escribir el evento en
una tabla dentro de la misma transaccion y publicarlo desde un proceso aparte.
Queda documentado como la evolucion del diseno, no implementado en esta entrega.

## Correrlo

Desde la raiz del repositorio:

```
docker compose up --build reglas
```

Levanta Pulsar, la base de reglas y el servicio en el puerto 8002. La semilla
carga tres partners al arrancar.

## Probarlo

Validar por HTTP, que es la utilidad de prueba:

```
curl -X POST localhost:8002/validaciones -H 'Content-Type: application/json' \
  -d '{"id_siniestro":"sin-1","partner_id":"seguros-alpes","monto":500000,"servicio":"plomeria","zona":"bogota-norte"}'
```

Validar por el topico, que es el camino real:

```
docker compose exec pulsar bin/pulsar-client produce \
  persistent://hogar-alpes/siniestros-b2b2c/comandos.reglas -m '...' 
```

Consultar:

```
curl localhost:8002/partners/seguros-alpes/reglas
curl localhost:8002/partners/seguros-alpes/validaciones
```

## Partners de la semilla

| partner | monto maximo | servicios | zonas |
|---|---|---|---|
| seguros-alpes | 8.000.000 COP | plomeria, electricidad, carpinteria | bogota-norte, bogota-centro, medellin |
| banco-andes | 2.500.000 COP | plomeria, electricidad | bogota-norte |
| comercio-muebles | 1.200.000 COP | carpinteria | cali, barranquilla |

Con esos tres se puede demostrar aprobacion y los cuatro motivos de rechazo.
