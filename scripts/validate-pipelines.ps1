param(
  [string]$Owner = "elizaaugusta4",
  [string]$Sha = "",
  [string[]]$Charts = @("cart","catalog","order","loki","promtail","tempo")
)

$ErrorActionPreference = 'Stop'

if (-not $Sha) {
  try {
    $Sha = (git rev-parse HEAD).Trim()
  } catch {
    throw "Unable to determine git SHA. Pass -Sha explicitly."
  }
}

Write-Host "== CI: helm lint/template ==" -ForegroundColor Cyan
foreach ($c in $Charts) {
  Write-Host "-- charts/$c" -ForegroundColor Gray
  helm lint "charts/$c" | Out-Host
  if ($LASTEXITCODE -ne 0) { throw "helm lint failed for charts/$c" }

  helm template "ci-$c" "charts/$c" | Out-Null
  if ($LASTEXITCODE -ne 0) { throw "helm template failed for charts/$c" }
}
Write-Host "Helm OK." -ForegroundColor Green

Write-Host "" 
Write-Host "== CD: docker bake file parse (print) ==" -ForegroundColor Cyan
$env:OWNER_LC = $Owner
$env:GIT_SHA = $Sha

docker buildx bake -f services/docker-bake.hcl --print | Out-Host
if ($LASTEXITCODE -ne 0) { throw "docker buildx bake --print failed" }
Write-Host "Bake file OK." -ForegroundColor Green

Write-Host "" 
Write-Host "== CD: GitOps patch (static validation) ==" -ForegroundColor Cyan

$tmpRoot = Join-Path $PWD ".tmp"
if (-not (Test-Path $tmpRoot)) {
  New-Item -ItemType Directory -Path $tmpRoot | Out-Null
}

$tmpDirName = "gitops-yq-" + [guid]::NewGuid().ToString("n")
$tmpDir = Join-Path $tmpRoot $tmpDirName
New-Item -ItemType Directory -Path $tmpDir | Out-Null

try {
  Copy-Item charts/catalog/values.yaml (Join-Path $tmpDir "catalog.values.yaml")
  Copy-Item charts/cart/values.yaml (Join-Path $tmpDir "cart.values.yaml")
  Copy-Item charts/order/values.yaml (Join-Path $tmpDir "order.values.yaml")

  $files = @(
    (Join-Path $tmpDir "catalog.values.yaml"),
    (Join-Path $tmpDir "cart.values.yaml"),
    (Join-Path $tmpDir "order.values.yaml")
  )

  foreach ($f in $files) {
    if (-not (Test-Path $f)) { throw "Missing temp file: $f" }
    $content = Get-Content -Raw $f
    if ($content -notmatch "(?m)^image:\s*$") { throw "Missing 'image' section in $f" }
    if ($content -notmatch "(?m)^\s+repository:\s*") { throw "Missing image.repository in $f" }
    if ($content -notmatch "(?m)^\s+tag:\s*") { throw "Missing image.tag in $f" }
  }

  Write-Host "Static GitOps file validation OK." -ForegroundColor Green
} finally {
  Remove-Item -Recurse -Force $tmpDir -ErrorAction SilentlyContinue
}

Write-Host "" 
Write-Host "All checks passed." -ForegroundColor Green
