#!/usr/bin/env bash
set -euo pipefail

echo "[verify] TypeScript SDK"
cd typescript-sdk
pnpm install --frozen-lockfile || pnpm install
pnpm run lint
pnpm run typecheck
pnpm run test -- --run
pnpm run build
cd ..

echo "[verify] Python SDK"
cd python-sdk
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
ruff check src tests
ruff format --check src tests
mypy src
pytest -q
python -m build
cd ..

echo "[verify] All checks passed"
