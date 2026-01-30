# Problemas Encontrados no Projeto

## 1. Integração e Observabilidade
- Dificuldade inicial para garantir que todos os serviços Python exportassem traces corretamente para o Tempo.
- Falta de propagação automática do contexto de trace entre serviços (necessidade de instrumentar requests e propagar headers manualmente).
- Configuração incorreta do endpoint OTLP (uso de /v1/traces ou porta errada).
- Falta de dependências do OpenTelemetry (ex: opentelemetry-instrumentation-requests).

## 2. Provisionamento e Deploy
- Dashboards do Grafana não eram provisionados automaticamente devido a problemas de montagem de volumes/configmaps.
- Erros de sintaxe em queries TraceQL nos dashboards provisionados.

## 3. Kubernetes
- Falta de nomes nas portas do Service do Tempo, impedindo upgrade via Helm.
- Pods não atualizavam após build/push sem rollout/restart dos deployments.

## 4. Troubleshooting
- Dificuldade inicial para correlacionar logs e traces (necessidade de padronizar trace_id nos logs).
- Dashboards com queries SQL-like em vez de TraceQL, causando erros de parsing.

