#!/usr/bin/env bash
set -euo pipefail

OWNER="${1:-elizaaugusta4}"
SHA="${2:-}"

if [[ -z "$SHA" ]]; then
  SHA="$(git rev-parse HEAD)"
fi

charts=(cart catalog order loki promtail tempo)

echo "== CI: helm lint/template =="
for c in "${charts[@]}"; do
  echo "-- charts/$c"
  helm lint "charts/$c" >/dev/null
  helm template "ci-$c" "charts/$c" >/dev/null
  echo "ok"
done

echo "Helm OK."

echo
echo "== CD: docker bake file parse (print) =="
OWNER_LC="${OWNER,,}" GIT_SHA="$SHA" docker buildx bake -f services/docker-bake.hcl --print >/dev/null

echo "Bake file OK."

echo
echo "== CD: GitOps patch (static validation) =="
for f in charts/catalog/values.yaml charts/cart/values.yaml charts/order/values.yaml; do
  grep -Eq '^image:' "$f"
  grep -Eq '^[[:space:]]+repository:' "$f"
  grep -Eq '^[[:space:]]+tag:' "$f"
done

echo "Static GitOps file validation OK."

echo
echo "All checks passed."
