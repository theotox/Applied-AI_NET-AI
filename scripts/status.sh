#!/usr/bin/env bash

echo "=== NetAI-Tools Status ==="

# Backend
if pgrep -f "uvicorn main:app" > /dev/null 2>&1; then
  BACKEND_PID=$(pgrep -f "uvicorn main:app" | head -1)
  echo "  Backend  : RUNNING (PID $BACKEND_PID)"
  curl -s http://127.0.0.1:8000/api/health 2>/dev/null \
    && echo "  Health   : OK" \
    || echo "  Health   : NOT RESPONDING"
else
  echo "  Backend  : STOPPED"
fi

# Frontend
if pgrep -f "vite" | grep -v grep > /dev/null 2>&1; then
  FRONTEND_PID=$(pgrep -f "vite" | head -1)
  echo "  Frontend : RUNNING (PID $FRONTEND_PID)"
  curl -s -o /dev/null -w "  HTTP     : %{http_code}" http://127.0.0.1:5173 2>/dev/null && echo ""
else
  echo "  Frontend : STOPPED"
fi
