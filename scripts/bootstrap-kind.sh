#!/usr/bin/env bash
set -euo pipefail


say() { printf "%b\n" "$*"; }
err() { printf "%b\n" "$*" 1>&2; }

need_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    err "[ERRO] Comando obrigatório não encontrado: $1"
    return 1
  fi
}

confirm() {
  local prompt="$1"
  local ans
  read -r -p "$prompt [y/N]: " ans || true
  [[ "${ans,,}" == "y" || "${ans,,}" == "yes" ]]
}

say "\nBootstrap do projeto (Kind + Docker + Helm + Observability)"
say "- Objetivo: automatizar a implantação do repo em um cluster Kind, criando namespaces, instalando Loki/Tempo/Promtail/Grafana e subindo os serviços."
say "- Requisitos: docker, kind, kubectl, helm." 

say "\nQual ambiente você está usando?"
say "  1) Windows (PowerShell / Git Bash / WSL)"
say "  2) Linux (bash)"
read -r -p "Escolha [1/2]: " ENV_CHOICE

case "${ENV_CHOICE}" in
  1) ENV_NAME="windows" ;;
  2) ENV_NAME="linux" ;;
  *) err "Escolha inválida. Use 1 (Windows) ou 2 (Linux)."; exit 2 ;;
esac

# Config padrão (ajuste via env vars)
KIND_CLUSTER_NAME="${KIND_CLUSTER_NAME:-virtual-store}"
NS_STORE="${NS_STORE:-virtual-store}"
NS_OBS="${NS_OBS:-observability}"

# Registry padrão (alinhado com Helm values e CD GitOps)
IMAGE_OWNER="${IMAGE_OWNER:-elizaaugusta4}"
IMAGE_PREFIX="${IMAGE_PREFIX:-ghcr.io/${IMAGE_OWNER}/distributed-tracing-python-kubernetes}"
TAG="${TAG:-latest}"

IMG_CATALOG="${IMAGE_PREFIX}/catalog:${TAG}"
IMG_CART="${IMAGE_PREFIX}/cart:${TAG}"
IMG_ORDER="${IMAGE_PREFIX}/order:${TAG}"

say "\nConfig:"
say "- kind cluster: ${KIND_CLUSTER_NAME}"
say "- namespace app: ${NS_STORE}"
say "- namespace observability: ${NS_OBS}"
say "- imagens:"
say "  - ${IMG_CATALOG}"
say "  - ${IMG_CART}"
say "  - ${IMG_ORDER}"

say "\nChecando dependências..."
need_cmd docker
need_cmd kind
need_cmd kubectl
need_cmd helm
say "OK."

say "\n[1/7] Criando/validando cluster kind..."
if kind get clusters | grep -qx "${KIND_CLUSTER_NAME}"; then
  say "- kind cluster '${KIND_CLUSTER_NAME}' já existe."
else
  kind create cluster --name "${KIND_CLUSTER_NAME}"
fi

say "\n[2/7] Criando namespaces..."
kubectl get ns "${NS_STORE}" >/dev/null 2>&1 || kubectl create namespace "${NS_STORE}"
kubectl get ns "${NS_OBS}" >/dev/null 2>&1 || kubectl create namespace "${NS_OBS}"

say "\n[3/7] Build das imagens (contexto ./services)..."
docker build -t "${IMG_CATALOG}" -f ./services/catalog/Dockerfile ./services

docker build -t "${IMG_CART}" -f ./services/cart/Dockerfile ./services

docker build -t "${IMG_ORDER}" -f ./services/order/Dockerfile ./services

say "\n[4/7] Carregando imagens no kind (sem registry)..."
# Preferir kind load (funciona em Linux/Windows)
kind load docker-image "${IMG_CATALOG}" --name "${KIND_CLUSTER_NAME}"
kind load docker-image "${IMG_CART}" --name "${KIND_CLUSTER_NAME}"
kind load docker-image "${IMG_ORDER}" --name "${KIND_CLUSTER_NAME}"

say "\n[5/7] Instalando stack de observabilidade (Tempo/Loki/Promtail/Grafana)..."
helm upgrade --install tempo ./charts/tempo --namespace "${NS_OBS}"
helm upgrade --install loki ./charts/loki --namespace "${NS_OBS}"
helm upgrade --install promtail ./charts/promtail --namespace "${NS_OBS}"

helm repo add prometheus-community https://prometheus-community.github.io/helm-charts >/dev/null 2>&1 || true
helm repo update >/dev/null 2>&1 || true
helm upgrade --install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  -n "${NS_OBS}" \
  -f ./charts/kube-prometheus-stack/values.yaml

kubectl apply -n "${NS_OBS}" -f ./charts/kube-prometheus-stack/dashboards

say "\n[6/7] Instalando serviços (Helm)..."
helm upgrade --install catalog ./charts/catalog --namespace "${NS_STORE}"
helm upgrade --install cart ./charts/cart --namespace "${NS_STORE}"
helm upgrade --install order ./charts/order --namespace "${NS_STORE}"

say "\n[7/7] Pós-setup (opcional)"
if confirm "Quer iniciar port-forward do Grafana em http://localhost:3000 agora?"; then
  if [[ "${ENV_NAME}" == "windows" ]] && command -v powershell.exe >/dev/null 2>&1; then
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./scripts/port-forward-grafana.ps1
  else
    say "Execute em outro terminal: kubectl -n ${NS_OBS} port-forward svc/kube-prometheus-stack-grafana 3000:80"
  fi
else
  say "- Grafana: execute ./scripts/port-forward-grafana.ps1 (Windows) ou: kubectl -n ${NS_OBS} port-forward svc/kube-prometheus-stack-grafana 3000:80"
fi

say "\nSetup concluído."
say "Próximos passos sugeridos:"
if [[ "${ENV_NAME}" == "windows" ]]; then
  say "- Gere tráfego: ./scripts/port-forward-order.ps1 e depois ./scripts/generate-traffic.ps1"
else
  say "- Gere tráfego: ./scripts/port-forward-order.sh e depois ./scripts/generate-traffic.sh"
fi
say "- No Grafana, use o dashboard de correlação e filtre por trace_id (32-hex)."
