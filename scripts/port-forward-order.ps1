param(
  [string]$Namespace = "virtual-store",
  [int]$LocalPort = 5002,
  [int]$RemotePort = 5002
)

$ErrorActionPreference = 'Stop'

Write-Host "Port-forward order service (svc/order) in namespace '$Namespace' to http://localhost:$LocalPort" -ForegroundColor Cyan
Write-Host "(Press Ctrl+C to stop)" -ForegroundColor Gray

kubectl -n $Namespace port-forward svc/order ${LocalPort}:$RemotePort
