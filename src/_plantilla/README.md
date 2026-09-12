# Plantilla de servicio — Hogar de los Alpes (Entrega 4)

Servicio de referencia para crear un microservicio nuevo (S10 Reglas, S7 Matching).
Trae el `seedwork` completo y un módulo `ejemplo/` con el flujo de punta a punta:

```
comando (HTTP o tópico) → agregado → evento de dominio → despachador Avro → tópico
                                    ↘ (lado lectura) proyección → query GET
```

## Por qué el seedwork se COPIA (no es un paquete compartido)

Cada servicio se despliega solo y no importa código de otro (regla dura de la
entrega). Compartir el seedwork como librería crearía acoplamiento en tiempo de
build y un punto único de cambio. Se copia a propósito: es la misma decisión que
"topología de datos descentralizada", pero para el código base.

## Qué trae la plantilla (dos mejoras sobre la E3, ya incorporadas)

1. **Cliente Pulsar reutilizado** (`seedwork/infraestructura/pulsar.py`): un solo
   `pulsar.Client` y un productor por tópico durante toda la vida del proceso
   (la E3 abría/cerraba cliente por mensaje → cuello de botella bajo el pico 4x).
2. **Consumidor robusto** (`seedwork/infraestructura/consumidores.py`):
   `Key_Shared` con `partition_key` = id de la entidad, `ack` **después** del
   commit de la Unidad de Trabajo, `negative_acknowledge` en error, e
   **idempotencia** por id de mensaje (`seedwork/infraestructura/idempotencia.py`)
   registrada en la misma transacción que el negocio. Además despacha por `type`
   del sobre a varios comandos. Ese trío responde al escenario 7.

## Convención de esquemas (namespace en BACKWARD)

Un **sobre Avro único por tópico** con discriminador `type` y un `data` con todos
los campos posibles, **opcionales con default**. Así hay un solo esquema por
tópico y el registry (en `BACKWARD`) rechaza un cambio incompatible. Ver
`modulos/ejemplo/infraestructura/schema/v1/`.

---

## Crear tu servicio en 5 pasos

1. **Copiar y renombrar.** `cp -R src/_plantilla src/<tu-servicio>` y renombra el
   módulo `modulos/ejemplo` por el tuyo (`modulos/<agregado>`). Ajusta los
   imports (`modulos.ejemplo` → `modulos.<agregado>`).

2. **Tópicos y BD en el `docker-compose.yml` de la raíz.** Descomenta tu servicio,
   apúntalo a tu `postgres-<servicio>` y define `TOPICO_COMANDOS`/`TOPICO_EVENTOS`
   con los nombres completos del namespace
   (`persistent://hogar-alpes/siniestros-b2b2c/<comandos|eventos>.<servicio>`).
   Esos tópicos ya los crea `infra/pulsar/crear_topicos.sh`.

3. **Escribir el agregado** en `modulos/<agregado>/dominio/`: entidades, objetos
   valor, eventos de dominio (participio pasado), reglas de negocio (invariantes),
   fábrica y la interfaz de repositorio. Reemplaza `Ejemplo`/`Nombre`/`EjemploCreado`.

4. **Escribir el esquema Avro** en `infraestructura/schema/v1/comandos.py` y
   `eventos.py`: un sobre por tópico con `type` + `data` (campos opcionales con
   default). Conecta los tipos en el `dict` de `manejadores` del consumidor.

5. **Cablear aplicación e infraestructura**: comando + handler (idempotencia por
   `id_mensaje`), query GET, DTO/mapeador/repositorio SQLAlchemy (CRUD),
   despachador (publica con `clave_particion` = id de la entidad) y las vistas de
   lectura. Escribe pruebas de las reglas en `tests/`.

## Probar la plantilla en aislado

```bash
cd src/_plantilla && pip install -r requirements.txt && pytest
```

Con el stack arriba (`docker compose up`), el flujo de demo:

```bash
# HTTP: crea un ejemplo y consulta la proyección
curl -X POST localhost:<puerto>/ejemplos -H 'Content-Type: application/json' -d '{"nombre":"demo"}'
curl localhost:<puerto>/ejemplos/<id>

# Broker: publica un comando en comandos.<servicio> y míralo consumido idempotentemente
```
