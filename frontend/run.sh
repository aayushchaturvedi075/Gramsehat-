#!/usr/bin/env bash
# ==============================================================================
# GramSehat - Frontend Server Runner
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

PORT="${PORT:-8080}"

echo "======================================================================"
echo " Starting GramSehat Frontend Server"
echo " Host: http://localhost:${PORT}"
echo " Serving Root: ${SCRIPT_DIR}"
echo "======================================================================"

exec python3 -m http.server "$PORT"
