; Data Mind Windows NSIS Installer Script
; Modern UI 2
!include "MUI2.nsh"
!include "FileFunc.nsh"

Name "Data Mind"
OutFile "DataMind_Setup_x64.exe"
InstallDir "$LOCALAPPDATA\Programs\DataMind"
InstallDirRegKey HKCU "Software\DataMind" "Install_Dir"
RequestExecutionLevel user

; Interface Configuration
!define MUI_ABORTWARNING
!define MUI_ICON "${NSISDIR}\Contrib\Graphics\Icons\modern-install.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"

Section "Install"
  SetOutPath "$INSTDIR"
  File /r "..\backend"
  File /r "..\frontend\dist"
  File /r "..\desktop"
  File "..\DataMind.bat"
  File "..\README.md"

  ; Create Shortcuts
  CreateDirectory "$SMPROGRAMS\Data Mind"
  CreateShortcut "$SMPROGRAMS\Data Mind\Data Mind.lnk" "$INSTDIR\DataMind.bat" "" "$INSTDIR\DataMind.bat" 0
  CreateShortcut "$SMPROGRAMS\Data Mind\Uninstall.lnk" "$INSTDIR\uninstall.exe" "" "$INSTDIR\uninstall.exe" 0
  CreateShortcut "$DESKTOP\Data Mind.lnk" "$INSTDIR\DataMind.bat" "" "$INSTDIR\DataMind.bat" 0

  ; Write Uninstaller
  WriteUninstaller "$INSTDIR\uninstall.exe"

  ; Registry
  WriteRegStr HKCU "Software\DataMind" "Install_Dir" "$INSTDIR"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\DataMind" "DisplayName" "Data Mind — Autonomous AI Data Analyst"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\DataMind" "UninstallString" "$INSTDIR\uninstall.exe"
SectionEnd

Section "Uninstall"
  Delete "$DESKTOP\Data Mind.lnk"
  Delete "$SMPROGRAMS\Data Mind\*.*"
  RMDir "$SMPROGRAMS\Data Mind"
  RMDir /r "$INSTDIR"
  DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\DataMind"
  DeleteRegKey HKCU "Software\DataMind"
SectionEnd

