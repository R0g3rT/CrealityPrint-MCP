; Installer fuer die inoffizielle MCP-Mod von Creality Print.
; Aufruf: makensis /DVERSION=7.3.1.0-mcp.1 /DSRCDIR=<build\OrcaSlicer> /DOUTFILE=<setup.exe> installer_mod.nsi
; Eigener Name, Ordner und Registry-Schluessel: beruehrt ein offizielles Creality Print nicht.

Unicode True
!include "MUI2.nsh"

!define APPNAME   "Creality Print MCP Mod"
!define REGKEY    "Software\Microsoft\Windows\CurrentVersion\Uninstall\CrealityPrintMCPMod"
!ifndef VERSION
  !error "VERSION fehlt (/DVERSION=...)"
!endif
!ifndef SRCDIR
  !error "SRCDIR fehlt (/DSRCDIR=...)"
!endif
!ifndef OUTFILE
  !define OUTFILE "CrealityPrint_${VERSION}_Setup.exe"
!endif

Name "${APPNAME} ${VERSION}"
OutFile "${OUTFILE}"
InstallDir "$PROGRAMFILES64\${APPNAME}"
InstallDirRegKey HKLM "${REGKEY}" "InstallLocation"
RequestExecutionLevel admin
SetCompressor /SOLID lzma

!define MUI_ICON   "${SRCDIR}\resources\images\CrealityPrint.ico"
!define MUI_UNICON "${SRCDIR}\resources\images\CrealityPrint.ico"
!define MUI_WELCOMEPAGE_TITLE "${APPNAME} ${VERSION}"
!define MUI_WELCOMEPAGE_TEXT "Inoffizielle Mod von Creality Print mit Remote API fuer MCP (Model Context Protocol).$\r$\n$\r$\nKeine offizielle Version von Creality. Gepflegt von R0g3rT, Lizenz AGPL-3.0.$\r$\n$\r$\nEin installiertes offizielles Creality Print bleibt unveraendert."
!define MUI_FINISHPAGE_RUN "$INSTDIR\CrealityPrint.exe"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "${SRCDIR}\LICENSE.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "German"
!insertmacro MUI_LANGUAGE "English"

Section "Install"
  SetShellVarContext all
  SetOutPath "$INSTDIR"
  File /r "${SRCDIR}\*.*"
  WriteUninstaller "$INSTDIR\Uninstall.exe"

  CreateDirectory "$SMPROGRAMS\${APPNAME}"
  CreateShortCut "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk" "$INSTDIR\CrealityPrint.exe"
  CreateShortCut "$SMPROGRAMS\${APPNAME}\Deinstallieren.lnk" "$INSTDIR\Uninstall.exe"
  CreateShortCut "$DESKTOP\${APPNAME}.lnk" "$INSTDIR\CrealityPrint.exe"

  WriteRegStr   HKLM "${REGKEY}" "DisplayName"     "${APPNAME}"
  WriteRegStr   HKLM "${REGKEY}" "DisplayVersion"  "${VERSION}"
  WriteRegStr   HKLM "${REGKEY}" "Publisher"       "R0g3rT (inoffizielle Mod von Creality Print)"
  WriteRegStr   HKLM "${REGKEY}" "DisplayIcon"     "$INSTDIR\CrealityPrint.exe"
  WriteRegStr   HKLM "${REGKEY}" "InstallLocation" "$INSTDIR"
  WriteRegStr   HKLM "${REGKEY}" "UninstallString" '"$INSTDIR\Uninstall.exe"'
  WriteRegStr   HKLM "${REGKEY}" "URLInfoAbout"    "https://github.com/R0g3rT/CrealityPrint-MCP"
  WriteRegDWORD HKLM "${REGKEY}" "NoModify" 1
  WriteRegDWORD HKLM "${REGKEY}" "NoRepair" 1
SectionEnd

Section "Uninstall"
  SetShellVarContext all
  Delete "$DESKTOP\${APPNAME}.lnk"
  RMDir /r "$SMPROGRAMS\${APPNAME}"
  RMDir /r "$INSTDIR"
  DeleteRegKey HKLM "${REGKEY}"
  ; Benutzereinstellungen (%APPDATA%\Creality\...) bleiben erhalten
SectionEnd
