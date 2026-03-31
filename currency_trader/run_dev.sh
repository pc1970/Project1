#!/usr/bin/env bash
# ── Development mode: backend + frontend with hot reload ──────────────────────
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"

echo "Starting Currency Trader Pro in development mode..."
echo "  Backend  → http://localhost:8765"
echo "  Frontend → http://localhost:5173  (Vite dev server)"
echo ""

# Backend
cd "$ROOT/backend"
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt -q
else
  source .venv/bin/activate
fi

python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8765 --reload &
BACKEND_PID=$!

# Frontend
cd "$ROOT/frontend"
npm install --silent
npm run dev &
FRONTEND_PID=$!

echo "Press Ctrl+C to stop both servers."
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
