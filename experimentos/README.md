# Experimentos de calidad — Entrega 5 (Parte A)

Scripts de carga (Locust) y procedimientos para ejecutar los tres escenarios de
calidad. El **diseño** de cada experimento (hipótesis, criterios) está en
[`../reportes/EXPERIMENTOS-E5.md`](../reportes/EXPERIMENTOS-E5.md); aquí está el
**cómo correrlos**.

## Requisitos

```bash
python -m venv .venv && source .venv/bin/activate     # o el venv del proyecto
pip install -r experimentos/requirements.txt
```

El sistema debe estar arriba. Para baseline local:

```bash
docker compose up -d --build          # 4 servicios + BFF (main actual)
# BFF queda en http://localhost:8004
```

`resultados/` guarda los CSV/HTML que produce Locust (ver `.gitkeep`).

---

## E1 — Escalabilidad (pico 4×)

Métrica central: **p99 de aceptación del POST** y **throughput (RPS)**. Se mide a
1× y a 4×, y luego se comparan las réplicas.

```bash
mkdir -p experimentos/resultados

# 1) Baseline 1x (1 réplica de siniestros)
locust -f experimentos/locustfile.py --host http://localhost:8004 \
    --headless -u 100 -r 20 -t 3m \
    --csv experimentos/resultados/e1_1x --html experimentos/resultados/e1_1x.html

# 2) Pico 4x con 1 réplica (muestra la degradación)
locust -f experimentos/locustfile.py --host http://localhost:8004 \
    --headless -u 400 -r 40 -t 3m \
    --csv experimentos/resultados/e1_4x_1rep --html experimentos/resultados/e1_4x_1rep.html

# 3) Pico 4x escalando siniestros a 3 réplicas (SIN tocar código)
docker compose up -d --scale siniestros=3
locust -f experimentos/locustfile.py --host http://localhost:8004 \
    --headless -u 400 -r 40 -t 3m \
    --csv experimentos/resultados/e1_4x_3rep --html experimentos/resultados/e1_4x_3rep.html
```

`-u` = usuarios concurrentes, `-r` = ritmo de arranque, `-t` = duración.
Ajusta `-u` hasta que 1× sea la tasa nominal y 4× su cuádruple.

**Verificación de 0 pérdida** (mensajes publicados == eventos persistidos):

```bash
# backlog del tópico (debe drenar a 0 al terminar)
docker compose exec pulsar bin/pulsar-admin topics stats persistent://public/default/comandos.siniestros

# eventos en el event store de S2
docker compose exec postgres-siniestros psql -U siniestros -d siniestros \
    -c "SELECT count(*) FROM eventos;"
```

---

## E2 — Modificabilidad (evolución de esquema Avro, BACKWARD)

No es de carga alta; es una demostración con carga baja constante mientras se
publica el esquema v2. Deja Locust corriendo suave de fondo:

```bash
locust -f experimentos/locustfile.py --host http://localhost:8004 \
    --headless -u 10 -r 2 -t 5m --csv experimentos/resultados/e2
```

Pasos (los ejecuta quien tenga el `schema/v2` listo — coordinar con S2):
1. Confirmar que consumidores (S10, S7, **S4**) corren con v1 y no se reinician.
2. Cambiar S2 a publicar `SiniestroRegistrado` v2 (campo nuevo con default).
3. Ver en logs que S10/S7/S4 siguen procesando (0 redespliegues).
4. Prueba negativa (falla segura):

```bash
# el broker debe RECHAZAR un esquema incompatible
docker compose exec pulsar bin/pulsar-admin schemas get \
    persistent://public/default/eventos.siniestros
```

---

## E3 — Disponibilidad (cae una réplica en mitad de la saga)

**Requiere el orquestador S4 + Saga Log (Partes C/D).** Con carga activa se mata
una réplica y se prueba con SQL que el Saga Log no deja transacciones huérfanas.

```bash
docker compose up -d --scale siniestros=2

# carga de fondo
locust -f experimentos/locustfile.py --host http://localhost:8004 \
    --headless -u 200 -r 40 -t 4m --csv experimentos/resultados/e3 &

# a mitad del run, matar una réplica de S2
sleep 60
docker stop $(docker compose ps -q siniestros | head -1)
```

**Evidencia con el Saga Log** (esto es lo que se muestra en el video):

```sql
-- ninguna saga debe quedar en estado intermedio al final
SELECT estado, count(*) FROM saga_log GROUP BY estado;
-- esperado: solo COMPLETADA / COMPENSADA; 0 en VALIDANDO / ASIGNANDO

-- transacciones que tardaron por la reentrega tras la caída
SELECT id_saga, siniestro_id, paso_actual, estado, fecha_actualizacion
FROM saga_log ORDER BY fecha_actualizacion DESC LIMIT 20;
```

> Ajusta el nombre de la tabla/campos (`saga_log`, `paso_actual`, `estado`…) al
> esquema real que definan C/D. El conector SQL exacto (usuario/BD del
> orquestador) se completa cuando el servicio esté en el compose.

---

## Qué queda registrado para la rúbrica

Por cada escenario: tabla **cuantitativa** (de los CSV de Locust: p50/p95/p99,
RPS, % fallos; y de SQL: conteos, tiempos de recuperación) + observación
**cualitativa** + **conclusión de hipótesis** (¿se cumplió?). Todo se vuelca en
el documento de resultados de la entrega.
