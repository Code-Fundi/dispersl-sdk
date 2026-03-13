#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${GITHUB_REF_NAME:-}" ]]; then
  echo "GITHUB_REF_NAME is required"
  exit 1
fi

echo "Running release preflight for tag ${GITHUB_REF_NAME}"
bash scripts/verify.sh
echo "Release preflight passed"
