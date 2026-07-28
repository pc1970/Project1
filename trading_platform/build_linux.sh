#!/usr/bin/env bash
# Build CurrencyTrader Pro for Linux (Debian/Ubuntu)
set -e

echo "=========================================="
echo "  CurrencyTrader Pro - Linux Build"
echo "=========================================="

# Require Python 3.10+
python3 --version || { echo "ERROR: Python 3 required"; exit 1; }

# Create venv
echo "[1/5] Creating virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

# Install deps
echo "[2/5] Installing dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q

# Install PyInstaller
echo "[3/5] Installing PyInstaller..."
pip install pyinstaller -q

# Build
echo "[4/5] Building executable..."
pyinstaller trading_platform.spec --clean --noconfirm

echo "[5/5] Done!"
echo ""
echo "Executable: $(pwd)/dist/CurrencyTraderPro"
echo ""
echo "Run with: ./dist/CurrencyTraderPro"
echo "Or set port: TRADING_PORT=9000 ./dist/CurrencyTraderPro"
