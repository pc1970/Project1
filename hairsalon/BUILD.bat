@echo off
title Glamour Hair Salon – Build EXE Installer
echo.
echo  ============================================
echo   Glamour Hair Salon – Building Windows EXE
echo  ============================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Install from https://python.org/downloads
    pause
    exit /b 1
)

:: Install dependencies
echo [1/4] Installing Python dependencies...
pip install -r requirements.txt --quiet
pip install pyinstaller --quiet

:: Run PyInstaller
echo [2/4] Building executable with PyInstaller...
pyinstaller --name GlamourSalon ^
    --onedir ^
    --noconsole ^
    --add-data "templates;templates" ^
    --add-data "static;static" ^
    --add-data "schema.sql;." ^
    --hidden-import flask ^
    --hidden-import flask_cors ^
    --hidden-import jinja2 ^
    --hidden-import dotenv ^
    app.py

if errorlevel 1 (
    echo ERROR: PyInstaller build failed.
    pause
    exit /b 1
)

:: Check for NSIS
echo [3/4] Looking for NSIS to build installer...
set NSIS_PATH=C:\Program Files (x86)\NSIS\makensis.exe
if not exist "%NSIS_PATH%" set NSIS_PATH=C:\Program Files\NSIS\makensis.exe

if exist "%NSIS_PATH%" (
    echo        NSIS found – building installer...
    "%NSIS_PATH%" installer.nsi
    if errorlevel 1 (
        echo WARNING: NSIS compile failed – skipping installer.
    ) else (
        echo        Installer created: GlamourSalonSetup-1.0.0.exe
    )
) else (
    echo        NSIS not found – skipping installer package.
    echo        Install NSIS from https://nsis.sourceforge.io to create a setup .exe
)

echo.
echo [4/4] Done!
echo.
echo  Standalone app:  dist\GlamourSalon\GlamourSalon.exe
if exist "GlamourSalonSetup-1.0.0.exe" (
    echo  Installer:       GlamourSalonSetup-1.0.0.exe
)
echo.
echo  Double-click GlamourSalon.exe to launch the salon app.
echo  Then open your browser at http://localhost:5000
echo.
pause
