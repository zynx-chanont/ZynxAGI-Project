#!/usr/bin/env bash
# Publish the ZYNX AGI FastAPI backend to a Hugging Face Space (Docker SDK).
#
# Usage:
#   export HF_TOKEN=hf_xxx          # write token from https://huggingface.co/settings/tokens
#   scripts/deploy_hf_space.sh <hf-username>/<space-name>
#
# The Space must already exist (create it at https://huggingface.co/new-space
# with SDK = Docker, Blank template). Only the backend package is uploaded.
set -euo pipefail

SPACE_ID="${1:-}"
if [[ -z "$SPACE_ID" || "$SPACE_ID" != */* ]]; then
  echo "Usage: $0 <hf-username>/<space-name>" >&2
  exit 1
fi
if [[ -z "${HF_TOKEN:-}" ]]; then
  echo "HF_TOKEN is not set (create a write token at https://huggingface.co/settings/tokens)" >&2
  exit 1
fi

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORK_DIR="$(mktemp -d)"
trap 'rm -rf "$WORK_DIR"' EXIT

HF_USER="${SPACE_ID%%/*}"
git clone --depth 1 "https://${HF_USER}:${HF_TOKEN}@huggingface.co/spaces/${SPACE_ID}" "$WORK_DIR/space"

cd "$WORK_DIR/space"
find . -mindepth 1 -maxdepth 1 ! -name .git ! -name .gitattributes -exec rm -rf {} +

cp "$REPO_ROOT/deploy/huggingface/Dockerfile" ./Dockerfile
cp "$REPO_ROOT/deploy/huggingface/README.md" ./README.md
rsync -a --exclude '__pycache__' --exclude '*.pyc' --exclude 'desktop.ini' \
  "$REPO_ROOT/zynx_agi/" ./zynx_agi/

git add -A
if git diff --cached --quiet; then
  echo "No changes to publish."
  exit 0
fi
git -c user.name="zynx-deploy" -c user.email="deploy@zynx.local" \
  commit -m "Deploy ZYNX AGI API from $(git -C "$REPO_ROOT" rev-parse --short HEAD)"
git push origin HEAD:main

echo "Pushed. Build logs: https://huggingface.co/spaces/${SPACE_ID}?logs=build"
echo "API URL: https://${HF_USER}-${SPACE_ID#*/}.hf.space (lowercase, '_' and '.' become '-')"
