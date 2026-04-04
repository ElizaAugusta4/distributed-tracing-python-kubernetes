#!/usr/bin/env bash
set -euo pipefail

NAMESPACE="${1:-virtual-store}"
LOCAL_PORT="${2:-5002}"
REMOTE_PORT="${3:-5002}"

echo "Port-forward order service (svc/order) in namespace '$NAMESPACE' to http://localhost:$LOCAL_PORT"
echo "(Press Ctrl+C to stop)"

kubectl -n "$NAMESPACE" port-forward svc/order "${LOCAL_PORT}:${REMOTE_PORT}"
