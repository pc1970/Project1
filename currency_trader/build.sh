#!/usr/bin/env bash
# ============================================================
# Currency Trader Pro — Build Script (Linux / macOS)
# ============================================================
set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"
FRONTEND="$ROOT/frontend"
BACKEND="$ROOT/backend"
STATIC="$ROOT/static"

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║   Currency Trader Pro — Build Script     ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# ── 1. Node / npm ─────────────────────────────────────────────────────────────
echo "▶  Checking Node.js..."
if ! command -v node &>/dev/null; then
  echo "✗  Node.js not found. Install from https://nodejs.org (v18+)" && exit 1
fi
NODE_VER=$(node -v | sed 's/v//')
echo "   Node.js $NODE_VER found."

# ── 2. Python ─────────────────────────────────────────────────────────────────
echo "▶  Checking Python..."
PYTHON=$(command -v python3 || command -v python)
if [ -z "$PYTHON" ]; then
  echo "✗  Python 3 not found." && exit 1
fi
echo "   Python found: $($PYTHON --version)"

# ── 3. Python venv & deps ─────────────────────────────────────────────────────
echo "▶  Installing Python dependencies..."
cd "$BACKEND"
if [ ! -d ".venv" ]; then
  $PYTHON -m venv .venv
fi
source .venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "   Python deps installed."

# ── 4. Frontend build ─────────────────────────────────────────────────────────
echo "▶  Building React frontend..."
cd "$FRONTEND"
npm install --silent
npm run build
echo "   Frontend built → $STATIC"

# ── 5. PyInstaller ────────────────────────────────────────────────────────────
echo "▶  Packaging with PyInstaller..."
cd "$ROOT"
pyinstaller currency_trader.spec --noconfirm
echo ""
echo "✔  Build complete!"
echo "   Executable: $ROOT/dist/currency_trader"
echo ""
echo "   Run with: ./dist/currency_trader"
deactivate
