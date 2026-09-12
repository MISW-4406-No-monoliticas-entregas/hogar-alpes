#!/usr/bin/env bash
# Configura la topología de Pulsar para Hogar de los Alpes (Entrega 4).
# Idempotente: se puede correr las veces que sea; los 409 (ya existe) se ignoran.
# Corre como servicio `pulsar-init` en el docker-compose, contra el broker.
set -uo pipefail

ADMIN_URL="${PULSAR_ADMIN_URL:-http://pulsar:8080}"
PA="bin/pulsar-admin --admin-url ${ADMIN_URL}"

TENANT="hogar-alpes"
NS="${TENANT}/siniestros-b2b2c"
CLUSTER="${PULSAR_CLUSTER:-standalone}"

log() { echo "[crear_topicos] $*"; }

# --- 1. Esperar a que el broker de admin responda ------------------------------
log "Esperando al broker en ${ADMIN_URL} ..."
for i in $(seq 1 30); do
  if curl -sf "${ADMIN_URL}/admin/v2/clusters" >/dev/null 2>&1; then
    log "Broker disponible."
    break
  fi
  sleep 3
  if [ "$i" -eq 30 ]; then log "El broker no respondió a tiempo."; exit 1; fi
done

# Ignora el error de "ya existe" (409/Conflict) y deja pasar los demás.
idempotente() {
  "$@" 2>/tmp/pa_err || grep -qiE "already exist|Conflict|409" /tmp/pa_err \
    || { log "ERROR ejecutando: $*"; cat /tmp/pa_err; }
}

# --- 2. Tenant y namespace -----------------------------------------------------
log "Tenant ${TENANT}"
idempotente $PA tenants create "${TENANT}" --allowed-clusters "${CLUSTER}"

log "Namespace ${NS}"
idempotente $PA namespaces create "${NS}"

# --- 3. Política de esquemas: BACKWARD ----------------------------------------
# Un sobre Avro único por tópico + BACKWARD => el registry rechaza cambios
# incompatibles. Es la base demostrable del escenario 6 (evolución de esquema).
log "Compatibilidad de esquemas = BACKWARD en ${NS}"
$PA namespaces set-schema-compatibility-strategy "${NS}" --compatibility BACKWARD
$PA namespaces set-is-allow-auto-update-schema "${NS}" --enable

# --- 4. Retención: 7 días / 1 GB ----------------------------------------------
# Permite reprocesar proyecciones y auditar durante las pruebas de la E5.
log "Retención = 7d / 1G en ${NS}"
$PA namespaces set-retention "${NS}" --time 7d --size 1G

# --- 5. Tópicos particionados (x4): los que reciben el pico 4x ----------------
for t in comandos.siniestros eventos.siniestros; do
  log "Tópico particionado (4): ${t}"
  idempotente $PA topics create-partitioned-topic "persistent://${NS}/${t}" -p 4
done

# --- 6. Tópicos sin particionar (por ahora) -----------------------------------
for t in comandos.reglas eventos.reglas comandos.matching eventos.matching eventos.partners; do
  log "Tópico: ${t}"
  idempotente $PA topics create "persistent://${NS}/${t}"
done

log "Topología lista."
$PA namespaces get-retention "${NS}" || true
$PA namespaces get-schema-compatibility-strategy "${NS}" || true
