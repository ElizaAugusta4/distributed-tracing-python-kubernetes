# Mapeamento do Projeto: Observabilidade com Kubernetes, Helm, Grafana, Tempo e Loki

## Visão Geral
Este arquivo documenta o mapeamento e o progresso do projeto, que visa criar uma arquitetura de múltiplos serviços monitorados por Grafana, Tempo e Loki, utilizando Kubernetes e Helm charts.

## 1. Arquitetura Inicial
- Múltiplos serviços (exemplo: Service A, Service B, Service C) comunicando entre si (HTTP/gRPC).
- Cada serviço será containerizado (Docker) e orquestrado via Kubernetes.
- Helm charts para deploy/configuração dos serviços e ferramentas.
- Observabilidade:
  - Grafana para dashboards
  - Tempo para traces
  - Loki para logs
  - Promtail para envio de logs

## 2. Componentes do Projeto
- Serviços de exemplo instrumentados com OpenTelemetry
- Helm charts customizados para cada serviço
- Helm charts para Grafana, Promtail, Tempo e Loki (charts oficiais)
- Configuração do Grafana para visualizar traces (Tempo) e logs (Loki)
- Documentação de deploy e arquitetura

## 3. Passos
-  Definir estrutura do projeto
-  Linguagem dos serviços da loja definida: Python
-  Implementação da Logica em python dos serviços da loja: catalog, cart e order. 
-  Instrumentar as aplicacoes para as ferramentas de obs
-  Buildar e rodar com um container localmente para validar se as aplicacoes da loja estão funcionais
-  Validar integração entre os serviços da loja
-  Criar imagens dos serviços e enviar para o Docker Hub 
-  Adicionar imagens geradas nos Charts dos Serviços da loja 
-  Validação dos charts
-  Criação do Cluster 
-  Switch para novo Cluster
-  Criação do namespace para os serviços da loja
-  Instalação dos serviços da loja
-  Validação dos Serviços da Loja, se estão funcionais
-  Criar namespace para stack de observabilidade 
-  Validar que as aplicacoes conseguem mandar traces para o tempo
-  Validar que os datasourcers do Grafana: Tempo e Loki estão se conectando com o grafana.
-  Acompanhar pelo Explorer com o Datasource Tempo o fluxo da requisição, onde as apis interagem.
-  Validar que o promtail e o loki se comunicam
-  Validar que o promtail está enviando logs para o loki
-  Validar que o Loki está apresentando as labels corretamenta no Explorer 
-  Garantir que as APPs estão mandando Traces ID
-  Criação de Dashboards importante para acompanhar a confiabilidade das apis
-  Adicionar o kube-prometheus-stack de observabilidade
-  Migrar Datasourcers do Grafana anterior para o novo
-  Migrar Dashboards para o kube-promtheus-stack
-  Criar SLIs e SLOs
-  Montar Runbook, Playbook, Handbook
-  GitOps com ArgoCD para deploy automatico
-  Hardenizacao dos servicos (probes, resources, securityContext)
-  Autoscaling e PDB por servico
-  Adicionar as pipelines CI e CD no repositório 
---
## 4. Critério de Saúde e Painel de Confiabilidade das APIs

Para garantir a confiabilidade do sistema, cada API possui como SLI, uma métrica principal monitorada via Prometheus e Grafana:

- **order**: taxa de erro 5xx
- **cart**: taxa de erro 5xx
- **catalog**: taxa de erro 5xx

Essas métricas são exibidas no painel "Erros 5xx por Serviço" do dashboard `incident-erros-logs-traces` no Grafana.

### Critério de SLO das APIs

- **order**: considerada saudável quando a taxa de erro 5xx é menor que 1% das requisições nos últimos 5 minutos.
- **cart**: considerada saudável quando a taxa de erro 5xx é menor que 1% das requisições nos últimos 5 minutos.
- **catalog**: considerada saudável quando a taxa de erro 5xx é menor que 1% das requisições nos últimos 5 minutos.

**Como visualizar:**
No Grafana, acesse o dashboard "Incidente – Erros, Logs e Traces" e observe o painel "Erros 5xx por Serviço". Se o valor estiver próximo de zero, a API está saudável.

