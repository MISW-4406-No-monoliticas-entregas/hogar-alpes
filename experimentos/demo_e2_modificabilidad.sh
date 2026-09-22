#!/usr/bin/env bash
# Demo del escenario E2 (Modificabilidad): evolución de esquema Avro sobre el
# broker real. Muestra: estrategia BACKWARD, v2 aditivo ACEPTADO, esquema
# incompatible RECHAZADO (HTTP 409) y consumidores sin redesplegar.
#
# Uso:  bash experimentos/demo_e2_modificabilidad.sh
set -euo pipefail
VM="${GCP_VM:-hogar-alpes-poc}"; ZONE="${GCP_ZONE:-us-central1-a}"
CO="sudo docker compose -f hogar-alpes/docker-compose.cluster.yml"
NS="hogar-alpes/siniestros-b2b2c"
TOPIC="persistent://$NS/eventos.siniestros"
PY="./.venv-experimentos/bin/python"
ssh() { gcloud compute ssh "$VM" --zone="$ZONE" --command="$1" 2>/dev/null; }

echo "== 1. Estrategia de compatibilidad del namespace =="
ssh "$CO exec -T broker1 bin/pulsar-admin namespaces get-schema-compatibility-strategy $NS" | tail -1

echo; echo "== 2. Versión actual del esquema registrado =="
ssh "$CO exec -T broker1 bin/pulsar-admin schemas get $TOPIC" > /tmp/e2_schema.txt
grep '"version"' /tmp/e2_schema.txt | head -1

# Nombre único por corrida -> el aditivo nunca choca (idempotente/repetible).
SUF="$(date +%H%M%S)"
# Construir v2 (aditivo, campo con default) y uno incompatible (requerido sin default)
E2SUF="$SUF" $PY - <<'PYEOF'
import json, os
suf=os.environ["E2SUF"]
txt=open('/tmp/e2_schema.txt').read(); js=txt[txt.index('{'):]
d=0
for i,c in enumerate(js):
    d+=(c=='{')-(c=='}')
    if d==0: js=js[:i+1]; break
avro=json.loads(js)['schemaInfo']['schema']; cl=lambda a: json.loads(json.dumps(a))
v2=cl(avro)
for f in v2['fields']:
    if f['name']=='data':
        f['type'][1]['fields'].append({"name":f"canal_origen_{suf}","type":"string","default":"web"})
open('/tmp/e2_v2.json','w').write(json.dumps({"type":"AVRO","schema":json.dumps(v2),"properties":{}}))
bad=cl(avro)
for f in bad['fields']:
    if f['name']=='data':
        f['type'][1]['fields'].append({"name":f"obligatorio_{suf}","type":"string"})  # sin default -> rompe BACKWARD
open('/tmp/e2_bad.json','w').write(json.dumps({"type":"AVRO","schema":json.dumps(bad),"properties":{}}))
PYEOF
gcloud compute scp /tmp/e2_v2.json /tmp/e2_bad.json "$VM":/tmp/ --zone="$ZONE" >/dev/null 2>&1
ssh "CID=\$($CO ps -q broker1); sudo docker cp /tmp/e2_v2.json \$CID:/tmp/e2_v2.json; sudo docker cp /tmp/e2_bad.json \$CID:/tmp/e2_bad.json" >/dev/null

echo; echo "== 3. Subir v2 (campo nuevo CON default) -> debe ACEPTAR =="
ssh "$CO exec -T broker1 bin/pulsar-admin schemas upload -f /tmp/e2_v2.json $TOPIC && echo '   -> v2 ACEPTADO'; $CO exec -T broker1 bin/pulsar-admin schemas get $TOPIC | grep '\"version\"' | head -1"

echo; echo "== 4. Subir esquema INCOMPATIBLE (requerido sin default) -> debe RECHAZAR =="
# El upload rechazado sale por stderr y termina en exit!=0; capturamos a variable
# (con '|| true') para que ni pipefail ni set -e nos engañen, y luego grepeamos.
BAD_OUT="$(gcloud compute ssh "$VM" --zone="$ZONE" \
   --command="$CO exec -T broker1 bin/pulsar-admin schemas upload -f /tmp/e2_bad.json $TOPIC" 2>&1 || true)"
if echo "$BAD_OUT" | grep -qiE 'HTTP 409|SchemaValidation|incompatible'; then
  echo "   -> RECHAZADO (HTTP 409, SchemaValidationException): falla segura en el registry"
else
  echo "   -> (no se detectó el rechazo; revisar manualmente)"
fi

echo; echo "== 5. Consumidores SIN redesplegar (uptime intacto) =="
ssh "$CO ps --format '{{.Service}} {{.Status}}'" | grep -E 'reglas|matching|orquestador' | grep -v postgres

echo; echo "Conclusión: BACKWARD + Avro con defaults -> se agrega un campo sin redesplegar; lo incompatible lo rechaza el broker."
