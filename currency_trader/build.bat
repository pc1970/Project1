@echo off
:: ============================================================
:: Currency Trader Pro — Build Script (Windows)
:: ============================================================
setlocal enabledelayedexpansion

set ROOT=%~dp0
set FRONTEND=%ROOT%frontend
set BACKEND=%ROOT%backend
set STATIC=%ROOT%static

echo.
echo ╔══════════════════════════════════════════╗
echo ║   Currency Trader Pro — Build Script     ║
echo ╚══════════════════════════════════════════╝
echo.

:: ── 1. Node ──────────────────────────────────────────────────────────────────
echo [1/5] Checking Node.js...
where node >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js not found. Install from https://nodejs.org
    pause & exit /b 1
)
for /f %%v in ('node -v') do echo        Node.js %%v found.

:: ── 2. Python ────────────────────────────────────────────────────────────────
echo [2/5] Checking Python...
where python >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python 3 not found.
    pause & exit /b 1
)
python --version

:: ── 3. Python venv & deps ─────────────────────────────────────────────────────
echo [3/5] Installing Python dependencies...
cd /d "%BACKEND%"
if not exist ".venv" python -m venv .venv
call .venv\Scripts\activate.bat
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo        Python deps installed.

:: ── 4. Frontend build ─────────────────────────────────────────────────────────
echo [4/5] Building React frontend...
cd /d "%FRONTEND%"
call npm install --silent
call npm run build
if errorlevel 1 ( echo ERROR: Frontend build failed. & pause & exit /b 1 )
echo        Frontend built.

:: ── 5. PyInstaller ────────────────────────────────────────────────────────────
echo [5/5] Packaging with PyInstaller...
cd /d "%ROOT%"
pyinstaller currency_trader.spec --noconfirm
if errorlevel 1 ( echo ERROR: PyInstaller failed. & pause & exit /b 1 )

echo.
echo ============================================================
echo  Build complete!
echo  Executable: %ROOT%dist\currency_trader.exe
echo ============================================================
echo.
call deactivate
pause
