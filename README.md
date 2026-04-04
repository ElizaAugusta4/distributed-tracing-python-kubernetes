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

## Quickstart (recomendado): setup automatizado
Este script automatiza a implantação em **Kind** usando **Docker + Helm + kubectl** (namespaces, observability stack e serviços).

### Pré-requisitos
- `docker`, `kind`, `kubectl`, `helm`
- **Windows**: Git Bash ou WSL para rodar o `.sh` (o script pergunta o ambiente)

### Executar
```bash
bash ./scripts/bootstrap-kind.sh
```

O script:
1) cria/usa o cluster Kind
2) cria namespaces `virtual-store` e `observability`
3) builda imagens a partir de `./services` (inclui `services/common`)
4) carrega imagens no Kind (sem precisar de registry)
5) instala Tempo/Loki/Promtail e kube-prometheus-stack
6) aplica dashboards
7) instala `catalog`, `cart`, `order`

## Acessar Grafana
No Windows (PowerShell):
```powershell
./scripts/port-forward-grafana.ps1
```

No Linux/macOS (bash):
```bash
./scripts/port-forward-grafana.sh
```

URL: http://localhost:3000

Senha (admin):
```sh
kubectl get secret -n observability kube-prometheus-stack-grafana -o jsonpath="{.data.admin-password}" | base64 -d
```

## Gerar tráfego (para ver logs/traces)
Port-forward do `order`:
```powershell
./scripts/port-forward-order.ps1
```

No Linux/macOS (bash):
```bash
./scripts/port-forward-order.sh
```

Depois gere tráfego:
```powershell
./scripts/generate-traffic.ps1 -BaseUrl http://localhost:5002 -Requests 80 -DelayMs 50
```

No Linux/macOS (bash):
```bash
./scripts/generate-traffic.sh http://localhost:5002 80 50
```

## CI/CD (GitOps)
- **CI**: valida charts (lint + template) em pull requests.
- **CD GitOps**: build/push de imagens no GHCR e commit automático atualizando `charts/*/values.yaml` com o `image.tag` (SHA). O **ArgoCD** sincroniza o cluster a partir do Git.

## GitOps com ArgoCD
Os manifests de ArgoCD estão em `./argocd` (app-of-apps + Applications por componente).

## Docs SRE
- `docs-sre/HANDBOOK.md`
- `docs-sre/PLAYBOOK.md`
- `docs-sre/RUNBOOK.md`

## Troubleshooting
- Veja `PROBLEMAS_ENCONTRADOS.md` para histórico de problemas e correções.
