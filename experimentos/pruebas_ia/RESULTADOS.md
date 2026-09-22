# Resultados — Pruebas no-determinísticas con IA (corrida real sobre GCP)

> Ejecutado contra el despliegue remoto (orquestador S4 en `http://<VM>:8005`).
> Generación no-determinística con el harness `invariantes.py` (P1) + un
> **subagente monitor** (IA) que actúa como oráculo: genera casos, vigila el Saga
> Log y verifica invariantes de dominio, reportando en lenguaje de negocio.

## Resumen de la corrida

| Fuente | Sagas | COMPLETADA | COMPENSADA | Huérfanas |
|---|---|---|---|---|
| Harness property-based (N=30, partner registrado) | 30 | 2 | 28 | 0 |
| Subagente — 8 sagas aleatorias (partners no registrados) | 8 | 0 | 8 | 0 |
| Subagente — adversarial (contrato) | 2 | 0 | 1 | 1 |
| **Total** | **40** | **2** | **37** | **1** |

## Invariantes de dominio (entradas válidas) — todos CUMPLEN

| Inv. | Propiedad | Veredicto |
|---|---|---|
| I1 Terminalidad | 0 sagas en estado intermedio | ✅ CUMPLE (38/38 terminales) |
| I2 No pérdida | toda saga iniciada es recuperable por id | ✅ CUMPLE |
| I3 Coherencia | COMPLETADA⇒proveedor+OK; COMPENSADA⇒sin proveedor+motivo+FALLIDO | ✅ CUMPLE (0 violaciones) |
| I4 Integridad | póliza/servicio/zona consultados == enviados | ✅ CUMPLE (0 violaciones) |

**El motor de orquestación es correcto bajo carga no-determinística.**

## Defectos encontrados por la IA (verificados manualmente)

Lo que las pruebas deterministas y la colección Postman **no** detectan, pero la
generación no-determinística sí:

### Defecto A (grave) — saga huérfana por monto negativo
- **Reproducción:** `POST /sagas {"partner_id":"seguros-alpes","poliza":"POL-1","monto":-500,"moneda":"COP","servicio":"plomeria","zona":"bogota-norte"}`
- **Observado:** responde `202`; la saga queda en `paso_actual=PENDIENTE`, `estado=EN_CURSO`, `siniestro_id=null`, `motivo_fallo=null` — indefinidamente (verificado >30 s).
- **Causa raíz:** el orquestador no valida el `monto` en el borde. La regla de
  dominio *"el monto estimado debe ser positivo"* no se aplica antes de arrancar
  la saga; S2 rechaza el `RegistrarSiniestro` inválido en silencio y la saga no
  tiene timeout/compensación para el paso que nunca confirma.
- **Lectura de negocio:** un siniestro con monto imposible es aceptado pero nunca
  se registra ni se compensa: la transacción larga queda colgada, ocupando el
  Saga Log sin desenlace. Rompe el invariante de terminalidad (I1).

### Defecto B (medio) — 500 ante tipo de dato equivocado
- **Reproducción:** `POST /sagas {... "monto":"mil" ...}` → `500 Internal Server Error`.
- **Causa raíz:** `float("mil")` revienta sin validación/casting defensivo; debería
  ser `400`.

### Hallazgo de negocio — partner desconocido nunca completa
Todas las sagas con un `partner_id` no dado de alta compensaron con motivo
"No hay reglas configuradas para el partner", **incluso** con cobertura de
proveedor. El desenlace no depende solo de (servicio, zona): la saga se rechaza
antes, en `ValidarSiniestro`, si el partner no existe. Es coherente (no un
defecto), pero conviene documentarlo: solo los partners sembrados
(`seguros-alpes`, `banco-andes`) llegan a `COMPLETADA`.

## Veredicto

- **Orquestación nominal de la saga: PASA** — I1–I4 sólidos en las 38 sagas de
  entrada válida, incluso bajo carga no-determinística.
- **Robustez del contrato de entrada: FALLA** — dos defectos (A y B) que deben
  corregirse validando el comando en el borde (regla `monto > 0` + casting) antes
  de iniciar la transacción larga. El defecto A es prioritario porque deja basura
  no compensable en el Saga Log.

## Valor demostrado

La prueba no-determinística asistida por IA encontró, sin casos escritos a mano,
dos defectos reales de robustez que la suite determinista y la colección Postman
(que pasan al 100 %) no exponen. El subagente actuó como generador + oráculo,
minimizó el caso y lo explicó en términos de negocio. Es el patrón recomendado:
invariantes de dominio como contrato, no aserciones de valor exacto.

> Decisión del equipo: los defectos se **reportan** a los dueños del orquestador
> (no se corrigen en esta iteración de Parte A para respetar la división del
> trabajo). Quedan con reproducción y caso mínimo para su corrección.
