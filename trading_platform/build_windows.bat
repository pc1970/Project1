@echo off
REM Build CurrencyTrader Pro for Windows
echo ==========================================
echo   CurrencyTrader Pro - Windows Build
echo ==========================================

python --version >nul 2>&1 || (echo ERROR: Python 3 required && exit /b 1)

echo [1/5] Creating virtual environment...
python -m venv .venv
call .venv\Scripts\activate.bat

echo [2/5] Installing dependencies...
pip install --upgrade pip -q
pip install -r requirements.txt -q

echo [3/5] Installing PyInstaller...
pip install pyinstaller -q

echo [4/5] Building executable...
pyinstaller trading_platform.spec --clean --noconfirm

echo [5/5] Done!
echo.
echo Executable: %CD%\dist\CurrencyTraderPro.exe
echo.
echo Run: dist\CurrencyTraderPro.exe
echo Or set port: set TRADING_PORT=9000 ^&^& dist\CurrencyTraderPro.exe
pause
