#!/usr/bin/env bash

echo "=== NetAI-Tools Stopping ==="

# Backend
if pgrep -f "uvicorn main:app" > /dev/null 2>&1; then
  BACKEND_PID=$(pgrep -f "uvicorn main:app" | head -1)
  echo "  Stopping backend (PID $BACKEND_PID)..."
  kill $BACKEND_PID 2>/dev/null
  echo "  Backend stopped."
else
  echo "  Backend is not running."
fi

# Frontend
if pgrep -f "vite" | grep -v grep > /dev/null 2>&1; then
  FRONTEND_PID=$(pgrep -f "vite" | head -1)
  echo "  Stopping frontend (PID $FRONTEND_PID)..."
  kill $FRONTEND_PID 2>/dev/null
  echo "  Frontend stopped."
else
  echo "  Frontend is not running."
fi

echo "=== Done ==="
