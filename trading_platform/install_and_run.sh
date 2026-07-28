#!/usr/bin/env bash
# Quick install and run (no build required - runs from source)
set -e
cd "$(dirname "$0")"

python3 -m venv .venv 2>/dev/null || true
source .venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt
python3 main.py
