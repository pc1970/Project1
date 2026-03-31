# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for Currency Trader Pro.
Run after building the React frontend: the ./static/ folder must exist.

  cd currency_trader
  pyinstaller currency_trader.spec
"""

import sys
import os
from pathlib import Path

ROOT = Path(SPECPATH)  # currency_trader/

block_cipher = None

a = Analysis(
    [str(ROOT / 'backend' / 'run.py')],
    pathex=[str(ROOT / 'backend')],
    binaries=[],
    datas=[
        # Bundle the compiled React frontend
        (str(ROOT / 'static'), 'static'),
    ],
    hiddenimports=[
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.loops.asyncio',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'anyio',
        'anyio._backends._asyncio',
        'aiosqlite',
        'sqlalchemy.dialects.sqlite',
        'sqlalchemy.ext.asyncio',
        'websockets',
        'websockets.legacy',
        'websockets.legacy.client',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'PIL', 'cv2', 'scipy'],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='currency_trader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,           # no terminal window on Windows
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
