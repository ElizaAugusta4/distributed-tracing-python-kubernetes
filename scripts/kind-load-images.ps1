param(
  [string]$KindClusterName = "",
  [string]$ImageOwner = "elizaaugusta4",
  [string]$Tag = "latest"
)

$ErrorActionPreference = 'Stop'

if (-not $KindClusterName) {
  $ctx = ""
  try {
    $ctx = (kubectl config current-context).Trim()
  } catch {
    $ctx = ""
  }

  if ($ctx -like "kind-*") {
    $KindClusterName = $ctx.Substring(5)
  } else {
    $KindClusterName = "kind"
  }
}

Write-Host "Loading local images into kind cluster '$KindClusterName'..." -ForegroundColor Cyan

$imagePrefix = "ghcr.io/$ImageOwner/distributed-tracing-python-kubernetes"

$images = @(
  "$imagePrefix/catalog:$Tag",
  "$imagePrefix/cart:$Tag",
  "$imagePrefix/order:$Tag"
)

foreach ($img in $images) {
  Write-Host "- kind load docker-image $img" -ForegroundColor Gray
  kind load docker-image $img --name $KindClusterName
}

Write-Host "Done." -ForegroundColor Green
