# Playbook – Operações e Resolução de Problemas

## Objetivo
Procedimentos detalhados para tarefas recorrentes e resolução de problemas comuns no ambiente de observabilidade.

## 1. Build e Deploy dos Serviços
- Build das imagens:
  ```sh
  docker build -t yourname/catalog:latest ./services/catalog
  docker build -t yourname/cart:latest ./services/cart
  docker build -t yourname/order:latest ./services/order
  ```
- Push para Docker Hub:
  ```sh
  docker push yourname/catalog:latest
  docker push yourname/cart:latest
  docker push yourname/order:latest
  ```
- Deploy no Kubernetes:
  ```sh
  helm upgrade --install <servico> ./charts/<servico> --namespace virtual-store
  ```

## 2. Provisionamento da Stack de Observabilidade
- Instale os charts:
  ```sh
  helm upgrade --install tempo ./charts/tempo --namespace observability
  helm upgrade --install loki ./charts/loki --namespace observability
  helm upgrade --install grafana ./charts/grafana --namespace observability
  helm install kube-prometheus-stack prometheus-community/kube-prometheus-stack -n observability -f ./kube-prometheus-stack/values.yaml
  ```
- Aplique dashboards customizados:
  ```sh
  kubectl apply -f ./kube-prometheus-stack/incident-erros-logs-traces-dashboard-cm.yaml -n observability
  kubectl apply -f ./kube-prometheus-stack/prometheus-cluster-dashboard-cm.yaml -n observability
  kubectl apply -f ./kube-prometheus-stack/prometheus-metrics-dashboard-cm.yaml -n observability
  kubectl apply -f ./kube-prometheus-stack/trace-log-correlation-dashboard-cm.yaml -n observability
  ```

## 3. Troubleshooting
- Verifique se os pods estão rodando:
  ```sh
  kubectl get pods -A
  ```
- Logs de um serviço:
  ```sh
  kubectl logs deployment/<servico> -n virtual-store
  ```
- Reinicie um serviço:
  ```sh
  kubectl rollout restart deployment/<servico> -n virtual-store
  ```

## 4. Dicas
- Sempre valide se as métricas e logs estão chegando no Grafana após qualquer alteração.
- Consulte o arquivo PROBLEMAS_ENCONTRADOS.md para histórico de problemas e soluções.

---
