param(
  [string]$Namespace = "observability",
  [int]$LocalPort = 3000
)

$ErrorActionPreference = 'Stop'

Write-Host "Port-forward Grafana in namespace '$Namespace' to http://localhost:$LocalPort" -ForegroundColor Cyan
Write-Host "(Press Ctrl+C to stop)" -ForegroundColor Gray

kubectl -n $Namespace port-forward svc/kube-prometheus-stack-grafana ${LocalPort}:80
