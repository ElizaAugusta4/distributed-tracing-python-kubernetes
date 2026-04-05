# Observabilidade em Microserviços Python no Kubernetes (Kind) com OpenTelemetry, Grafana, Tempo e Loki

Projeto de Observabilidade em Python(SRE/Observability) para demonstrar:
- Tracing distribuído (OpenTelemetry) com propagação entre serviços
- Logs no Loki com `trace_id` real (32-hex) para correlação com traces no Tempo
- Grafana como “single pane of glass” (logs ↔ traces)
- Deploy via Helm e opção GitOps via ArgoCD

## Componentes
- **Serviços**
	- `catalog`: produtos
	- `cart`: carrinho
	- `order`: pedidos/orquestração
- **Observabilidade**
	- **Tempo** (traces), **Loki** (logs), **Promtail** (scrape/ship), **Grafana** (dashboards)
- **Kubernetes**
	- Cluster local com **Kind** (foco em reproduzibilidade)
	- Charts Helm em `./charts`

## Dashboards
- **Observabilidade – Logs e Traces por Serviço**: visão geral com filtros `namespace`, `app`, `trace_id`
- **Incidente – Erros, Logs e Traces**: foco em incident response (erros 5xx + drill down)

## Setup manual (Kind + Helm)

### Pré-requisitos
- `docker`, `kind`, `kubectl`, `helm`

### Criar cluster e namespaces
```bash
kind create cluster --name virtual-store
kubectl create namespace virtual-store
kubectl create namespace observability
```

### Instalar observabilidade (Tempo/Loki/Promtail/Grafana)
```bash
helm upgrade --install tempo ./charts/tempo --namespace observability
helm upgrade --install loki ./charts/loki --namespace observability
helm upgrade --install promtail ./charts/promtail --namespace observability

helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm upgrade --install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
	-n observability \
	-f ./charts/kube-prometheus-stack/values.yaml

kubectl apply -n observability -f ./charts/kube-prometheus-stack/dashboards
```

### Build e deploy dos serviços
1) Build local das imagens (a partir de `./services`):
```bash
docker build -t catalog:local -f ./services/catalog/Dockerfile ./services
docker build -t cart:local -f ./services/cart/Dockerfile ./services
docker build -t order:local -f ./services/order/Dockerfile ./services
```

2) Carregar imagens no Kind:
```bash
kind load docker-image catalog:local --name virtual-store
kind load docker-image cart:local --name virtual-store
kind load docker-image order:local --name virtual-store
```

3) Instalar os charts (ajuste a tag/repo conforme necessário):
```bash
helm upgrade --install catalog ./charts/catalog -n virtual-store \
	--set image.repository=catalog --set image.tag=local
helm upgrade --install cart ./charts/cart -n virtual-store \
	--set image.repository=cart --set image.tag=local
helm upgrade --install order ./charts/order -n virtual-store \
	--set image.repository=order --set image.tag=local
```

## Acessar Grafana
```bash
kubectl -n observability port-forward svc/kube-prometheus-stack-grafana 3000:80
```

URL: http://localhost:3000

Senha (admin):
```bash
kubectl get secret -n observability kube-prometheus-stack-grafana -o jsonpath="{.data.admin-password}" | base64 -d
```

## Gerar tráfego (para ver logs/traces)
1) Port-forward do `order`:
```bash
kubectl -n virtual-store port-forward svc/order 5002:5002
```

2) Em outro terminal, gere requisições:
```bash
for i in $(seq 1 80); do
	curl -s -X POST http://localhost:5002/order \
		-H 'content-type: application/json' \
		-d '{"product_id":"p1","quantity":1}' >/dev/null
	sleep 0.05
done
```

## CI/CD (GitOps)

### CI (quality gate)
- Workflow: `.github/workflows/ci.yaml`
- Quando roda: em **push** e em **pull request**
- O que faz: para cada chart da lista (`cart`, `catalog`, `order`, `loki`, `promtail`, `tempo`) executa:
	- `helm lint` (pega erros de chart/values)
	- `helm template` (garante que o chart renderiza)

**Objetivo**: falhar rápido quando um chart quebra, sem precisar de cluster.

### CD GitOps (build + publish + bump)
- Workflow: `.github/workflows/cd-gitops.yaml`
- Quando roda: **push na `main`** quando muda:
	- `services/**` (código/Dockerfiles dos serviços)
	- `.github/workflows/cd-gitops.yaml` (o próprio pipeline)

O CD faz 3 coisas em sequência:
1) **Build e push** das imagens no GHCR usando `docker buildx bake` definido em `services/docker-bake.hcl`
2) **Atualiza** `charts/*/values.yaml` com `image.repository` e `image.tag = <SHA do commit>`
3) **Commit/push** dessas mudanças (`chore(gitops): deploy <sha>`) para o ArgoCD sincronizar

**Por que não vira loop infinito?**
- O CD não roda quando muda `charts/**`.
- Então o commit automático de “bump” não re-dispara o CD.


## GitOps com ArgoCD
Os manifests de ArgoCD estão em `./argocd` (app-of-apps + Applications por componente).

## Docs SRE
- `docs-sre/HANDBOOK.md`
- `docs-sre/PLAYBOOK.md`
- `docs-sre/RUNBOOK.md`

## Troubleshooting
- Veja `PROBLEMAS_ENCONTRADOS.md` para histórico de problemas e correções.
