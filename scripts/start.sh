#!/usr/bin/env bash
set -e

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"
LOG_DIR="$PROJECT_DIR/logs"

mkdir -p "$LOG_DIR"

echo "=== NetAI-Tools Starting ==="

# -- Backend --
echo "[1/2] Starting backend (uvicorn)..."
cd "$BACKEND_DIR"
source ../venv/bin/activate 2>/dev/null || true
nohup uvicorn main:app --host 0.0.0.0 --port 8000 --reload \
  > "$LOG_DIR/backend.log" 2>&1 &
BACKEND_PID=$!
echo "  Backend PID: $BACKEND_PID (logs: $LOG_DIR/backend.log)"

# -- Frontend --
echo "[2/2] Starting frontend (vite)..."
cd "$FRONTEND_DIR"
nohup npm run dev \
  > "$LOG_DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo "  Frontend PID: $FRONTEND_PID (logs: $LOG_DIR/frontend.log)"

echo ""
echo "=== Ready ==="
echo "  Frontend : http://localhost:5173"
echo "  Backend  : http://localhost:8000"
echo "  Health   : http://localhost:8000/api/health"
echo "  API Docs : http://localhost:8000/docs"
echo ""
echo "  Stop with: kill $BACKEND_PID $FRONTEND_PID"
