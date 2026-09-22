#!/usr/bin/env bash
# Crea la VM de Google Compute Engine para desplegar el POC (cluster de Pulsar).
# Requisitos: gcloud instalado y autenticado (`gcloud auth login`) y un proyecto
# con facturación/créditos educativos. NO guarda credenciales en el repo.
#
# Uso:
#   export GCP_PROJECT=<tu-proyecto>
#   bash infra/gcp/crear_vm.sh
set -euo pipefail

PROJECT="${GCP_PROJECT:?Define GCP_PROJECT con el id de tu proyecto de GCP}"
ZONE="${GCP_ZONE:-us-central1-a}"
VM="${GCP_VM:-hogar-alpes-poc}"
# e2-standard-4 = 4 vCPU / 16 GB. Suficiente para zk + 2 bookies + 2 brokers +
# 4 postgres + 4 servicios. ~USD 0,13/h: apagar la VM cuando no se use.
MACHINE="${GCP_MACHINE:-e2-standard-4}"
TAG="hogar-alpes"

echo "==> Proyecto=${PROJECT} Zona=${ZONE} VM=${VM} Maquina=${MACHINE}"
gcloud config set project "${PROJECT}" >/dev/null

# --- 1. Firewall: solo las APIs de los servicios y el admin de Pulsar ---------
# Los puertos binarios de Pulsar (6650/6651) NO se exponen: los clientes son los
# propios servicios, dentro de la VM. Restringir --source-ranges a tu IP en real.
echo "==> Regla de firewall (tag ${TAG})"
if ! gcloud compute firewall-rules describe "${TAG}-apis" >/dev/null 2>&1; then
  gcloud compute firewall-rules create "${TAG}-apis" \
    --direction=INGRESS --action=ALLOW \
    --rules=tcp:8000-8005,tcp:8080,tcp:8081 \
    --source-ranges="${FIREWALL_SOURCE:-0.0.0.0/0}" \
    --target-tags="${TAG}" \
    --description="APIs de los servicios (8000-8003), BFF (8004), orquestador S4 (8005) y admin de Pulsar (8080/8081)"
else
  echo "    (la regla ${TAG}-apis ya existe)"
fi

# --- 2. VM Debian 12 con Docker instalado por startup-script ------------------
echo "==> Creando la VM (Debian 12 + Docker por startup-script)"
gcloud compute instances create "${VM}" \
  --zone="${ZONE}" \
  --machine-type="${MACHINE}" \
  --image-family=debian-12 --image-project=debian-cloud \
  --boot-disk-size=30GB --boot-disk-type=pd-balanced \
  --tags="${TAG}" \
  --metadata=startup-script='#!/bin/bash
set -e
if ! command -v docker >/dev/null 2>&1; then
  apt-get update
  apt-get install -y ca-certificates curl git
  install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
  chmod a+r /etc/apt/keyrings/docker.asc
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian $(. /etc/os-release && echo $VERSION_CODENAME) stable" > /etc/apt/sources.list.d/docker.list
  apt-get update
  apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
  usermod -aG docker $(ls /home | head -n1) || true
fi'

echo "==> VM creada. IP pública:"
gcloud compute instances describe "${VM}" --zone="${ZONE}" \
  --format="get(networkInterfaces[0].accessConfigs[0].natIP)"
echo "==> Espera ~1 min a que el startup-script instale Docker, luego: bash infra/gcp/desplegar.sh"
