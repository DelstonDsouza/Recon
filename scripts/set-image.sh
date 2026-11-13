#!/usr/bin/env bash
# Usage: bash scripts/set-image.sh <env> <tag> <image>
set -euo pipefail

ENV="$1"
TAG="$2"
IMAGE="$3"
FILE="apps/podinfo/overlays/${ENV}/kustomization.yaml"

# the images block is the last block in the file: remove it and rewrite it
sed -i '/^images:/,$d' "$FILE"
cat >> "$FILE" << YAML
images:
  - name: ghcr.io/stefanprodan/podinfo
    newName: ${IMAGE}
    newTag: ${TAG}
YAML

echo "Set ${ENV} -> ${IMAGE}:${TAG}"
