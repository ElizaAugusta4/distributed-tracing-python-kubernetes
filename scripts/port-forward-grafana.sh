#!/usr/bin/env bash
set -euo pipefail

NAMESPACE="${1:-observability}"
LOCAL_PORT="${2:-3000}"

echo "Port-forward Grafana (svc/kube-prometheus-stack-grafana) in namespace '$NAMESPACE' to http://localhost:$LOCAL_PORT"
echo "(Press Ctrl+C to stop)"

kubectl -n "$NAMESPACE" port-forward svc/kube-prometheus-stack-grafana "${LOCAL_PORT}:80"
