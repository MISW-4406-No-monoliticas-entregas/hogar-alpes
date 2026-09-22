#!/usr/bin/env bash
# Despliega el POC en la VM de GCP: clona el repo (o hace pull) y levanta el
# cluster con docker-compose.cluster.yml. Idempotente: se puede correr de nuevo.
#
# Uso:
#   export GCP_PROJECT=<tu-proyecto>
#   bash infra/gcp/desplegar.sh
set -euo pipefail

PROJECT="${GCP_PROJECT:?Define GCP_PROJECT}"
ZONE="${GCP_ZONE:-us-central1-a}"
VM="${GCP_VM:-hogar-alpes-poc}"
REPO="${REPO_URL:-https://github.com/MISW-4406-No-monoliticas-entregas/hogar-alpes.git}"
BRANCH="${REPO_BRANCH:-main}"

gcloud config set project "${PROJECT}" >/dev/null

echo "==> Clonando/actualizando el repo y levantando el cluster en ${VM}"
gcloud compute ssh "${VM}" --zone="${ZONE}" --command="
  set -e
  # Si el directorio no existe o quedó como copia sin git (deploy viejo), re-clona.
  if [ ! -d hogar-alpes/.git ]; then
    sudo rm -rf hogar-alpes
    git clone --branch ${BRANCH} ${REPO} hogar-alpes
  fi
  cd hogar-alpes
  git fetch origin ${BRANCH} && git checkout ${BRANCH} && git pull --ff-only
  # docker necesita sudo la primera vez (antes de que el grupo aplique en la sesión)
  sudo docker compose -f docker-compose.cluster.yml up -d --build
  echo '--- estado ---'
  sudo docker compose -f docker-compose.cluster.yml ps
"

IP=$(gcloud compute instances describe "${VM}" --zone="${ZONE}" \
  --format="get(networkInterfaces[0].accessConfigs[0].natIP)")
echo "==> Desplegado. Prueba de humo:"
echo "    curl http://${IP}:8001/salud        # S9 Integraciones"
echo "    curl http://${IP}:8000/salud        # S2 Siniestros"
echo "    Pulsar admin: http://${IP}:8080/admin/v2/persistent/hogar-alpes/siniestros-b2b2c"
echo "    Apaga la VM cuando termines:  gcloud compute instances stop ${VM} --zone=${ZONE}"
