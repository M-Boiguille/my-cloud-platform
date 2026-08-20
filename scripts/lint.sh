#!/usr/bin/env bash
set -euo pipefail

echo "==> Ruff"
. .venv/bin/activate
ruff check .

echo "==> Mypy"
mypy core/ career.py
