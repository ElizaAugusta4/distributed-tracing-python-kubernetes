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
3. **Instale os charts via Helm e aplique os dashboards:**
   ```sh
   helm upgrade --install tempo ./charts/tempo --namespace observability
   helm upgrade --install loki ./charts/loki --namespace observability
   helm upgrade --install grafana ./charts/grafana --namespace observability
   helm upgrade --install catalog ./charts/catalog --namespace virtual-store
   helm upgrade --install cart ./charts/cart --namespace virtual-store
   helm upgrade --install order ./charts/order --namespace virtual-store
   helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
   helm repo update
   helm install kube-prometheus-stack prometheus-community/kube-prometheus-stack -n observability -f ./kube-prometheus-stack/values.yaml

   # Aplique os ConfigMaps dos dashboards customizados
   kubectl apply -f ./kube-prometheus-stack/incident-erros-logs-traces-dashboard-cm.yaml -n observability
   kubectl apply -f ./kube-prometheus-stack/prometheus-cluster-dashboard-cm.yaml -n observability
   kubectl apply -f ./kube-prometheus-stack/prometheus-metrics-dashboard-cm.yaml -n observability
   kubectl apply -f ./kube-prometheus-stack/trace-log-correlation-dashboard-cm.yaml -n observability
   ```
4. **Acesse o Grafana:**
   - Usuário padrão: `admin`
   - Senha: Verifique no secret do grafana a senha 
   - URL: http://localhost:3000

## GitOps com ArgoCD (fase 1)
Esta opcao deixa o deploy com cara de producao, usando GitOps para sincronizar os charts.

1. **Instale o ArgoCD via Helm:**
   ```sh
   helm repo add argo https://argoproj.github.io/argo-helm
   helm repo update
   kubectl create namespace argocd
   helm upgrade --install argocd argo/argo-cd -n argocd -f ./argocd/values.yaml
   ```
2. **Aplique os Applications:**
   ```sh
   kubectl apply -n argocd -f ./argocd/applications
   ```
3. **Acesso ao ArgoCD:**
   - Ingress padrao: http://argocd.local (requer ingress controller)
   - Alternativa via port-forward:
     ```sh
     kubectl port-forward svc/argocd-server -n argocd 8080:80
     ```

## Troubleshooting
- Veja o arquivo `PROBLEMAS_ENCONTRADOS.md` para um histórico dos principais desafios e soluções.
- Use os dashboards provisionados para investigação rápida de incidentes.

