#!/usr/bin/env bash
set -euo pipefail

echo "==> Pytest"
. .venv/bin/activate
pytest || {
  code=$?
  if [ "$code" -eq 5 ]; then
    echo "Aucun test trouvé. Ce n'est pas une erreur."
    exit 0
  fi
  exit "$code"
}
