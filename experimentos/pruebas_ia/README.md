# Pruebas no-determinísticas asistidas por IA (extra)

> Propuesta sugerida por el profesor: usar IA (p. ej. Claude Code como agente)
> para complementar las pruebas deterministas con **pruebas exploratorias de
> entrada e itinerario no-determinístico**, donde la IA genera los casos y actúa
> como oráculo para interpretar el resultado.

## Por qué, para este sistema

Las pruebas unitarias del repo son deterministas (entradas fijas, aserciones
fijas). En una arquitectura basada en eventos con una saga de larga duración,
los defectos interesantes aparecen con **combinaciones y tiempos que nadie
escribió a mano**: formatos de partner raros, órdenes de eventos inusuales,
fallos inyectados en momentos arbitrarios. Ahí una IA aporta dos cosas:

1. **Generación no-determinística de entradas/itinerarios** (fuzzing dirigido,
   metamórfico, caos) — mucha más variedad que casos escritos a mano.
2. **Oráculo semántico**: en vez de comparar contra un valor fijo, la IA verifica
   que se cumplan **invariantes de dominio** y explica una violación en términos
   del negocio (DDD), proponiendo el caso mínimo que la reproduce.

Todas se anclan en **invariantes**, no en salidas exactas — que es lo que hace
válida una prueba no-determinística.

## Las cuatro pruebas propuestas

### P1 · Property-based sobre la saga (incluida, ejecutable)
La IA genera N solicitudes de saga con `servicio/zona/monto/partner` aleatorios
y verifica invariantes de dominio contra las BD y el Saga Log:
- **Terminalidad:** toda saga POSTeada termina en `COMPLETADA` o `COMPENSADA` (0 huérfanas).
- **No pérdida:** nº de sagas aceptadas == nº de filas en `saga_log`.
- **Coherencia de desenlace:** `COMPLETADA` ⇒ tiene `proveedor_id`; `COMPENSADA` ⇒ sin proveedor y con `motivo_fallo`.
- **Idempotencia:** reenviar la misma `(partner_id, poliza)` no crea una saga duplicada.

Ver `invariantes.py`. La no-determinación está en la generación aleatoria; el
agente puede ampliar el espacio de entradas y diagnosticar cualquier violación.

### P2 · Fuzzing del ACL de partners (S9)
La IA genera payloads de partner **malformados o inusuales** (campos faltantes,
tipos equivocados, unicode, montos negativos/enormes, formatos nuevos de partner)
y verifica que S9: acepta los válidos, **rechaza los inválidos con 4xx sin
caerse**, y nunca publica un comando con `monto ≤ 0` o sin `poliza`. Invariante:
"ninguna entrada, por rara que sea, deja a S9 en 5xx ni produce un siniestro
que viole las reglas del agregado".

### P3 · Metamórfico sobre el ACL (invariancia de traducción)
La IA toma un mismo siniestro lógico y lo expresa en los **dos formatos de
partner** (`seguros-alpes` y `banco-andes`) — y en variantes que ella inventa.
Invariante metamórfico: siniestros lógicamente equivalentes deben producir el
**mismo estado de dominio** (mismo monto, misma póliza normalizada), sin importar
el formato de entrada. Detecta fugas en el anticorruption layer.

### P4 · Caos no-determinístico (disponibilidad)
La IA, durante carga, **inyecta fallos en momentos y objetivos aleatorios**
(matar una réplica de S2, pausar un consumidor, duplicar un mensaje) y luego
verifica la **convergencia**: el Saga Log llega a un estado consistente (0
huérfanas, 0 pérdida). Generaliza el experimento E3 a fallos elegidos por la IA
en vez de un `docker stop` fijo.

## Cómo se usan con Claude Code (el agente)

- **Generador + oráculo:** el agente propone lotes de entradas (P1–P3) o de
  fallos (P4), ejecuta el harness, lee el JSON de resultados y las BD, y decide
  si algún invariante se rompió; si sí, minimiza el caso y lo reporta en lenguaje
  de dominio.
- **Bucle exploratorio:** se puede correr en `/loop` para que el agente siga
  variando el espacio de casos hasta que K rondas seguidas no encuentren nada
  nuevo (loop-until-dry), registrando qué cubrió.

## Ejecutar la prueba incluida (P1)

Con el stack arriba (`docker compose up -d`):

```bash
./.venv-experimentos/bin/python experimentos/pruebas_ia/invariantes.py --n 40
```

Sale un resumen JSON con cada invariante y su veredicto; código de salida ≠ 0 si
alguno falla (apto para CI y para que el agente lo interprete).
