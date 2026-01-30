# Mapeamento do Projeto: Observabilidade com Kubernetes, Helm, Grafana, Tempo e Loki

## Visão Geral
Este arquivo documenta o mapeamento e o progresso do projeto, que visa criar uma arquitetura de múltiplos serviços monitorados por Grafana, Tempo e Loki, utilizando Kubernetes e Helm charts.

---

## 1. Arquitetura Inicial
- Múltiplos serviços (exemplo: Service A, Service B) comunicando entre si (HTTP/gRPC).
- Cada serviço será containerizado (Docker) e orquestrado via Kubernetes.
- Helm charts para deploy/configuração dos serviços e ferramentas.
- Observabilidade:
  - Grafana para dashboards
  - Tempo para traces
  - Loki para logs

## 2. Componentes do Projeto
- Serviços de exemplo instrumentados com OpenTelemetry
- Helm charts customizados para cada serviço
- Helm charts para Grafana, Tempo e Loki (charts oficiais)
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
-  Validar que os datasourcers do Grafana: Tempo e Loki estão se conectando
-  Acompanhar pelo Explorer com o Datasource Tempo o fluxo da requisição, onde as apis interagem.
-  Criação de Dashboards importante para acompanhar a confiabilidade das apis
---

