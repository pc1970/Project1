"""
Build a standalone Windows executable with PyInstaller.

Usage (run from the hairsalon/ directory):
    python build_windows.py

Output:
    dist/GlamourSalon/GlamourSalon.exe   (standalone folder)
    dist/GlamourSalon.exe                (single-file exe, slower cold start)

Requirements:
    pip install pyinstaller
"""

import subprocess
import sys
import os
import shutil

ROOT = os.path.dirname(os.path.abspath(__file__))

def run(cmd):
    print(f'>> {" ".join(cmd)}')
    result = subprocess.run(cmd, cwd=ROOT)
    if result.returncode != 0:
        sys.exit(result.returncode)


def main():
    # Clean previous build artifacts
    for d in ('build', 'dist'):
        path = os.path.join(ROOT, d)
        if os.path.exists(path):
            shutil.rmtree(path)
            print(f'Removed {d}/')

    run([
        sys.executable, '-m', 'PyInstaller',
        '--name', 'GlamourSalon',
        '--onedir',                      # folder build (faster startup than --onefile)
        '--noconsole',                   # hide console window on Windows
        '--add-data', f'templates{os.pathsep}templates',
        '--add-data', f'static{os.pathsep}static',
        '--add-data', f'schema.sql{os.pathsep}.',
        '--hidden-import', 'flask',
        '--hidden-import', 'flask_cors',
        '--hidden-import', 'jinja2',
        '--hidden-import', 'dotenv',
        '--hidden-import', 'twilio',
        'app.py',
    ])

    print('\nBuild complete!')
    print(f'Executable: {os.path.join(ROOT, "dist", "GlamourSalon", "GlamourSalon.exe")}')
    print('Next step: run installer.nsi with NSIS to create an installer package.')


if __name__ == '__main__':
    main()
