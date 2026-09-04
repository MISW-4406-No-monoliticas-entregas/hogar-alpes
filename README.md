# Trabajos Siniestros

Microservicio de la plataforma **Hogar de los Alpes** encargado de recibir los
siniestros que envían los partners (aseguradoras, bancos, comercios) y gestionar
su ciclo de vida. Forma parte de la línea de negocio B2B2C, que concentra el 70 %
del volumen de la plataforma.

El servicio está diseñado con **Domain-Driven Design**, **arquitectura hexagonal**
y **comunicación basada en eventos**, priorizando escalabilidad, modificabilidad
y disponibilidad.

## Arquitectura

El servicio se organiza en dos módulos que no se conocen entre sí y se comunican
únicamente a través de eventos de dominio:

- **`siniestros`** — lado de escritura. Contiene el agregado `Siniestro` y toda
  la lógica de negocio. Recibe comandos, aplica las invariantes del dominio,
  persiste el estado y emite eventos de dominio.
- **`seguimiento`** — lado de lectura (CQRS). Mantiene una proyección
  desnormalizada del estado de cada siniestro, optimizada para consulta, que se
  actualiza reaccionando a los eventos que emite `siniestros`.
  
Cada evento de dominio se despacha de dos maneras complementarias:

1. **En proceso**, mediante un mediador de señales, para actualizar la proyección
   del módulo `seguimiento`.
2. **Hacia el broker**, traducido a un evento de integración con esquema Avro y
   publicado en el tópico `eventos.trabajos`, para que lo consuma el resto de los
   microservicios de la plataforma.

El comando `RegistrarSiniestro` puede llegar tanto por HTTP como por el tópico
`comandos.siniestros`, porque en producción la carga real entra por el broker.

## Modelo de dominio

- **Agregado raíz:** `Siniestro`, con entidades hijas `Evidencia` y `Actividad`.
- **Objetos valor:** `Direccion`, `Monto`, `EstadoSiniestro`, `Poliza`, `PartnerId`.
- **Comandos:** `RegistrarSiniestro`, `AsignarProveedor`.
- **Eventos de dominio:** `SiniestroRegistrado`, `ProveedorAsignado`.
- **Reglas de negocio** (invariantes del agregado):
  - la póliza es obligatoria,
  - el monto estimado debe ser positivo,
  - un siniestro solo puede asignarse a un proveedor si está en estado registrado.

## Decisiones de diseño

- **Arquitectura hexagonal.** El dominio no depende de infraestructura ni del
  framework web; las dependencias apuntan siempre hacia el dominio. La API y los
  consumidores del broker son adaptadores de entrada; el repositorio y el
  despachador de eventos son adaptadores de salida. El ensamblado de adaptadores
  concretos se hace en la capa de aplicación y al arrancar la app.

- **CQRS y separación comando/consulta.** La escritura (`siniestros`) y la lectura
  (`seguimiento`) tienen modelos, tablas y rutas de código distintas. Esto permite
  escalar la ingesta y la consulta de forma independiente, algo clave dado el
  volumen del negocio (25 millones de peticiones diarias de partners, con picos
  de hasta 4x durante eventos climáticos).

- **Comunicación por eventos, sin acoplamiento entre módulos.** `seguimiento` se
  suscribe a los eventos de dominio por su nombre, a través del mediador de
  señales del `seedwork`, y nunca importa clases del módulo `siniestros`. Ambos
  módulos solo comparten el nombre y la forma del evento como contrato.

- **La Unidad de Trabajo es la única que publica eventos.** El agregado acumula
  sus eventos de dominio pero no los emite; la Unidad de Trabajo los despacha
  después de confirmar la transacción, de modo que nada se publica si la
  persistencia falla.

- **Fábrica del agregado.** Encapsula el ensamblado del `Siniestro` y aplica las
  invariantes en la construcción, garantizando que ningún siniestro exista en un
  estado inválido.

- **Esquemas Avro versionados (`schema/v1/`).** Los eventos de integración usan un
  esquema versionado. La evolución retrocompatible (añadir campos opcionales en un
  `schema/v2`) permite cambiar el contrato sin romper a los consumidores.

- **`seedwork` con las clases base.** Concentra las abstracciones de DDD
  (entidad, agregación raíz, objeto valor, evento de dominio, regla de negocio,
  fábrica, repositorio, Unidad de Trabajo, mediadores) compartidas por los módulos.

## Stack tecnológico

- **Python 3.12 + Flask** para el adaptador HTTP.
- **SQLAlchemy sobre PostgreSQL** como persistencia. Dos tablas: `siniestros`
  (escritura) y `estado_siniestro` (lectura).
- **Apache Pulsar** como event broker, con esquemas **Avro** para los mensajes.
  En desarrollo corre en modo `standalone`; en producción sería un clúster
  multi-zona.
- **PyDispatcher** para el mediador de eventos de dominio en proceso.

## Estructura del proyecto

```
src/siniestros/
  api/                 Adaptador HTTP (Flask): blueprints y create_app
  config/              Conexion a PostgreSQL y settings por variables de entorno
  seedwork/            Clases base compartidas (DDD)
    dominio/           Entidad, AgregacionRaiz, ObjetoValor, EventoDominio,
                       ReglaNegocio, Fabrica, Repositorio, excepciones, mixins
    aplicacion/        Comando/Query y sus mediadores, mediador de eventos de
                       dominio, DTO, Mapeador, ServicioAplicacion
    infraestructura/   Unidad de Trabajo, UoW SQLAlchemy, bases Pulsar/Avro
    presentacion/      Manejo de errores de la API
  modulos/
    siniestros/        Escritura: dominio, aplicacion (comandos), infraestructura
    seguimiento/       Lectura (CQRS): proyeccion, queries, handlers
  main.py              Arranca Flask y el consumidor de comandos.siniestros
```

## Configuración

Toda la configuración se toma de variables de entorno; el repositorio no contiene
credenciales. Los valores por defecto son de desarrollo y coinciden con los del
`docker-compose.yml`.

| Variable | Default | Descripción |
|---|---|---|
| `DATABASE_URL` | (vacío) | URL completa de la base; si se define, tiene prioridad |
| `DB_HOST` / `DB_PORT` | `localhost` / `5432` | PostgreSQL |
| `DB_USER` / `DB_PASSWORD` / `DB_NAME` | `siniestros` | Credenciales de desarrollo |
| `PULSAR_URL` | `pulsar://localhost:6650` | Broker |
| `TOPICO_EVENTOS` | `eventos.trabajos` | Eventos de integración (salida) |
| `TOPICO_COMANDOS` | `comandos.siniestros` | Comandos por broker (entrada) |
| `CONSUMIR_COMANDOS` | `true` | Arranca el consumidor de comandos |

## Cómo ejecutar

```bash
docker compose up --build
```

Levanta tres contenedores: PostgreSQL, Apache Pulsar (standalone) y el servicio.
El servicio está listo cuando `GET /salud` responde `{"estado":"ok"}`.

### Flujo de ejemplo

Registrar un siniestro (comando por HTTP):

```bash
curl -X POST http://localhost:5000/siniestros \
  -H "Content-Type: application/json" \
  -d '{"partner_id":"aseguradora-1","poliza":"POL-123","monto":500000,
       "moneda":"COP","calle":"Cra 7 # 1-2","ciudad":"Bogota"}'
```

Consultar el estado (lee la proyección de `seguimiento`):

```bash
curl http://localhost:5000/siniestros/<id>
curl http://localhost:5000/partners/aseguradora-1/siniestros
```

Asignar un proveedor:

```bash
curl -X POST http://localhost:5000/siniestros/<id>/proveedor \
  -H "Content-Type: application/json" -d '{"proveedor_id":"prov-9"}'
```

Observar el evento de integración publicado en el broker:

```bash
docker compose exec pulsar bin/pulsar-client consume eventos.trabajos \
  -s lector-demo -n 0
```

## API

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/siniestros` | Registra un siniestro |
| `POST` | `/siniestros/<id>/proveedor` | Asigna un proveedor a un siniestro |
| `GET`  | `/siniestros/<id>` | Estado de un siniestro (proyección) |
| `GET`  | `/partners/<id>/siniestros` | Siniestros de un partner (proyección) |
| `GET`  | `/salud` | Verificación de disponibilidad |

## Pruebas

```bash
pip install -r requirements.txt
pytest
```

La suite cubre las reglas de negocio del agregado de forma aislada y el flujo de
eventos entre módulos (comando → evento de dominio → proyección → consulta).

## Escenarios de calidad

Sobre este servicio se ejecutan los escenarios de los atributos de calidad
priorizados:

- **Ingesta bajo carga (escalabilidad).** Ráfaga de comandos `RegistrarSiniestro`
  por `comandos.siniestros`. El consumidor usa suscripción `Shared`, de modo que
  varias réplicas del servicio reparten la carga.
- **Consulta bajo carga (escalabilidad).** Ráfaga de consultas sobre la proyección
  `estado_siniestro`. Al estar separada de la escritura, puede escalarse con
  réplicas de lectura sin afectar la ingesta.
- **Pérdida de una réplica (disponibilidad).** Se da de baja una réplica del
  servicio o del broker. Pulsar reentrega los mensajes no confirmados a otra
  réplica y la reconexión a PostgreSQL se recupera automáticamente, de modo que
  el sistema sigue atendiendo.

En producción, Pulsar correría como clúster multi-zona y el servicio se
desplegaría con varias réplicas detrás de un balanceador.
