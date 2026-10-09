#!/usr/bin/env bash
# ==============================================================================
# GramSehat - Backend Server Runner
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate virtual environment if present
if [ -d "venv" ]; then
    echo "Activating virtual environment: venv"
    source venv/bin/activate
elif [ -d "../venv" ]; then
    echo "Activating virtual environment: ../venv"
    source ../venv/bin/activate
fi

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"

echo "======================================================================"
echo " Starting GramSehat Backend API"
echo " Host: http://${HOST}:${PORT}"
echo " Interactive Docs: http://${HOST}:${PORT}/docs"
echo " Endpoints:"
echo "   - POST /transcribe-audio          (Layer 2: Voice STT via Sarvam AI Saaras v3)"
echo "   - POST /extract-report-text       (Layer 2: Prescription/Report OCR via EasyOCR)"
echo "   - POST /assess-urgency            (Layer 5: Safety Rule Engine - Deterministic WHO/IMCI)"
echo "   - POST /process-transcript        (Receives Web Speech API transcript text)"
echo "   - POST /structure-symptoms        (Layer 4: AI Symptom Structuring - Flash)"
echo "   - POST /explain-report            (Layer 4: AI Lab/Prescription Explanation - Pro)"
echo "   - POST /generate-hospital-summary (Layer 4: AI SBAR Hospital Handover - Pro)"
echo "   - GET  /health                    (Service Status & Health Check)"
echo "======================================================================"

exec uvicorn app.main:app --host "$HOST" --port "$PORT" --lifespan on
