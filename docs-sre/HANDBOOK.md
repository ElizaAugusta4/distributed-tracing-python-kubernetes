# Handbook – Visão Geral e Boas Práticas

## Objetivo
Referência para entendimento do projeto, arquitetura, responsabilidades e boas práticas de operação e evolução.

## 1. Arquitetura
- Microserviços Python: catalog, cart, order
- Observabilidade: OpenTelemetry, Tempo, Loki, Grafana
- Orquestração: Kubernetes + Helm

## 2. Fluxo de Observabilidade
- Cada serviço exporta traces e logs com trace_id
- Tempo armazena traces, Loki armazena logs
- Grafana centraliza visualização e dashboards

## 3. Boas Práticas
- Sempre instrumente novos serviços com OpenTelemetry
- Padronize logs para incluir trace_id
- Use dashboards simples e objetivos para confiabilidade
- Documente critérios de saúde antes de criar alertas
- Mantenha o PROJETO_MAPEAMENTO.md atualizado

## 4. Evolução
- Antes de criar novos dashboards, valide os existentes
- Implemente alertas apenas após garantir confiabilidade básica
- Use o PLAYBOOK para tarefas operacionais e troubleshooting
- Use o RUNBOOK para resposta rápida a incidentes

## 5. Limites de Recursos (virtual-store)

Para deixar o lab mais realista e reduzir risco de "noisy neighbor" dentro do namespace `virtual-store`, aplicamos:

- **ResourceQuota**: limita consumo total do namespace (CPU/mem, pods, services, etc.)
- **LimitRange**: define defaults e guardrails por container (requests/limits, min/max)

### Onde configurar

- Chart: `charts/virtual-store-namespace-limits`
- Valores: `charts/virtual-store-namespace-limits/values.yaml`
- Aplicação GitOps (ArgoCD): `argocd/applications/virtual-store-namespace-limits.yaml`

### Valores padrão

- ResourceQuota (hard):
	- `requests.cpu`: `4`
	- `requests.memory`: `4Gi`
	- `limits.cpu`: `8`
	- `limits.memory`: `8Gi`
	- `pods`: `30`
	- `services`: `20`
	- `persistentvolumeclaims`: `5`

- LimitRange (Container):
	- defaultRequest: `cpu=100m`, `memory=128Mi`
	- default: `cpu=500m`, `memory=256Mi`
	- min: `cpu=10m`, `memory=64Mi`
	- max: `cpu=2`, `memory=1Gi`

### Como ajustar

1) Ajuste os valores em `charts/virtual-store-namespace-limits/values.yaml`
2) Commit + push
3) Sincronize a app `virtual-store-namespace-limits` no ArgoCD

### Como validar

- `kubectl -n virtual-store describe resourcequota virtual-store-resourcequota`
- `kubectl -n virtual-store describe limitrange virtual-store-limitrange`

---
