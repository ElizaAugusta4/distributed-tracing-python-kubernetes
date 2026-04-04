param(
  [string]$BaseUrl = "http://localhost:5002",
  [int]$Requests = 50,
  [int]$DelayMs = 0
)

$ErrorActionPreference = 'Stop'

Write-Host "Generating traffic against order service at $BaseUrl ($Requests requests)..." -ForegroundColor Cyan

$postOk = 0
$postErr = 0
$getOk = 0
$getErr = 0

for ($i = 1; $i -le $Requests; $i++) {
  $userId = (Get-Random -Minimum 1 -Maximum 6)
  try {
    $body = @{ user_id = "$userId" } | ConvertTo-Json -Compress
    Invoke-RestMethod -Method Post -Uri "$BaseUrl/orders" -ContentType "application/json" -Body $body | Out-Null
    $postOk++
  } catch {
    $postErr++
  }

  try {
    Invoke-RestMethod -Method Get -Uri "$BaseUrl/orders" | Out-Null
    $getOk++
  } catch {
    $getErr++
  }

  if ($DelayMs -gt 0) {
    Start-Sleep -Milliseconds $DelayMs
  }
}

Write-Host "Done." -ForegroundColor Green
Write-Host "POST /orders: ok=$postOk err=$postErr" -ForegroundColor Gray
Write-Host "GET  /orders: ok=$getOk  err=$getErr" -ForegroundColor Gray
Write-Host "Now check Grafana dashboards (Logs/Traces) for fresh data." -ForegroundColor Green
