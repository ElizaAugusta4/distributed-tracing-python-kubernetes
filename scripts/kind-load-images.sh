#!/usr/bin/env bash
set -euo pipefail

KIND_CLUSTER_NAME="${KIND_CLUSTER_NAME:-}"
IMAGE_OWNER="${IMAGE_OWNER:-elizaaugusta4}"
TAG="${TAG:-latest}"

if [[ -z "$KIND_CLUSTER_NAME" ]]; then
  ctx="$(kubectl config current-context 2>/dev/null || true)"
  if [[ "$ctx" == kind-* ]]; then
    KIND_CLUSTER_NAME="${ctx#kind-}"
  else
    KIND_CLUSTER_NAME="kind"
  fi
fi

image_prefix="ghcr.io/${IMAGE_OWNER}/distributed-tracing-python-kubernetes"
images=(
  "${image_prefix}/catalog:${TAG}"
  "${image_prefix}/cart:${TAG}"
  "${image_prefix}/order:${TAG}"
)

echo "Loading local images into kind cluster '${KIND_CLUSTER_NAME}'..."
for img in "${images[@]}"; do
  echo "- kind load docker-image $img"
  kind load docker-image "$img" --name "$KIND_CLUSTER_NAME"
done

echo "Done."
