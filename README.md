# Observabilidade em Microserviços Python com Kubernetes, Helm, Grafana, Tempo e Loki

## Visão Geral
Este projeto demonstra uma arquitetura de microserviços Python (catalog, cart, order) instrumentados com OpenTelemetry, rodando em Kubernetes e monitorados por uma stack de observabilidade moderna: Grafana, Tempo e Loki.

## Componentes
- **Serviços:**
  - `catalog`: gerenciamento de produtos
  - `cart`: gerenciamento de carrinhos
  - `order`: gerenciamento de pedidos e orquestração
- **Observabilidade:**
  - **OpenTelemetry**: tracing distribuído em todos os serviços
  - **Tempo**: backend de traces
  - **Loki**: backend de logs
  - **Grafana**: dashboards, traces e logs correlacionados
- **Infraestrutura:**
  - Deploy via Helm charts customizados
  - Imagens Docker publicadas no Docker Hub
  - Orquestração em Kubernetes (Kind)

## Dashboards
- Correlação entre traces e logs (trace_id)

## Como rodar
1. **Build e push das imagens:**
   ```sh
   docker build -t yourname/catalog:latest ./services/catalog
   docker build -t yourname/cart:latest ./services/cart
   docker build -t yourname/order:latest ./services/order
   docker push yourname/catalog:latest
   docker push yourname/cart:latest
   docker push yourname/order:latest
   ```
2. **Crie o cluster Kubernetes e namespaces:**
   ```sh
   kubectl create namespace virtual-store
   kubectl create namespace observability
   ```
3. **Instale os charts via Helm:**
   ```sh
   helm upgrade --install tempo ./charts/tempo --namespace observability
   helm upgrade --install loki ./charts/loki --namespace observability
   helm upgrade --install grafana ./charts/grafana --namespace observability
   helm upgrade --install catalog ./charts/catalog --namespace virtual-store
   helm upgrade --install cart ./charts/cart --namespace virtual-store
   helm upgrade --install order ./charts/order --namespace virtual-store
   ```
4. **Acesse o Grafana:**
   - Usuário padrão: `admin` / `admin`
   - URL: http://localhost:3000

## Troubleshooting
- Veja o arquivo `PROBLEMAS_ENCONTRADOS.md` para um histórico dos principais desafios e soluções.
- Use os dashboards provisionados para investigação rápida de incidentes.

