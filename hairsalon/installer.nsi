; ============================================================
; Glamour Hair Salon – NSIS Windows Installer Script
; ============================================================
; Prerequisites:
;   1. Run  python build_windows.py  first (creates dist\GlamourSalon\)
;   2. Install NSIS 3.x  (https://nsis.sourceforge.io)
;   3. Compile:  makensis installer.nsi
; ============================================================

!define APP_NAME      "Glamour Hair Salon"
!define APP_VERSION   "1.0.0"
!define APP_PUBLISHER "Glamour Hair Salon"
!define APP_EXE       "GlamourSalon.exe"
!define APP_DIR       "dist\GlamourSalon"
!define INSTALL_DIR   "$PROGRAMFILES64\GlamourHairSalon"
!define UNINSTALLER   "Uninstall.exe"
!define REG_KEY       "Software\Microsoft\Windows\CurrentVersion\Uninstall\GlamourHairSalon"

; ── Metadata ────────────────────────────────────────────────
Name          "${APP_NAME}"
OutFile       "GlamourSalonSetup-${APP_VERSION}.exe"
InstallDir    "${INSTALL_DIR}"
InstallDirRegKey HKLM "${REG_KEY}" "InstallDir"
RequestExecutionLevel admin

; ── Modern UI ───────────────────────────────────────────────
!include "MUI2.nsh"

!define MUI_ABORTWARNING

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"

; ── Installer ───────────────────────────────────────────────
Section "Install" SecInstall
  SetOutPath "$INSTDIR"

  ; Copy all files from the PyInstaller output folder
  File /r "${APP_DIR}\*.*"

  ; Copy .env.example so users can configure credentials
  File ".env.example"

  ; Write uninstaller
  WriteUninstaller "$INSTDIR\${UNINSTALLER}"

  ; Registry entries for Add/Remove Programs
  WriteRegStr   HKLM "${REG_KEY}" "DisplayName"      "${APP_NAME}"
  WriteRegStr   HKLM "${REG_KEY}" "DisplayVersion"    "${APP_VERSION}"
  WriteRegStr   HKLM "${REG_KEY}" "Publisher"         "${APP_PUBLISHER}"
  WriteRegStr   HKLM "${REG_KEY}" "InstallDir"        "$INSTDIR"
  WriteRegStr   HKLM "${REG_KEY}" "UninstallString"   "$INSTDIR\${UNINSTALLER}"
  WriteRegStr   HKLM "${REG_KEY}" "DisplayIcon"       "$INSTDIR\${APP_EXE}"
  WriteRegDWORD HKLM "${REG_KEY}" "NoModify"          1
  WriteRegDWORD HKLM "${REG_KEY}" "NoRepair"          1

  ; Desktop shortcut
  CreateShortcut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}" "" "$INSTDIR\${APP_EXE}" 0

  ; Start Menu shortcut
  CreateDirectory "$SMPROGRAMS\${APP_NAME}"
  CreateShortcut  "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk"   "$INSTDIR\${APP_EXE}"
  CreateShortcut  "$SMPROGRAMS\${APP_NAME}\Uninstall.lnk"     "$INSTDIR\${UNINSTALLER}"

  ; Auto-open browser after launch (optional launch script)
  MessageBox MB_ICONINFORMATION "Installation complete!$\n$\nLaunch '${APP_NAME}' from the desktop shortcut.$\nThe app will open at http://localhost:5000 in your browser."
SectionEnd

; ── Uninstaller ─────────────────────────────────────────────
Section "Uninstall"
  Delete "$INSTDIR\${UNINSTALLER}"
  RMDir  /r "$INSTDIR"

  Delete "$DESKTOP\${APP_NAME}.lnk"
  RMDir  /r "$SMPROGRAMS\${APP_NAME}"

  DeleteRegKey HKLM "${REG_KEY}"
SectionEnd
