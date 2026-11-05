$ErrorActionPreference = "Stop"

$RootPath = (Get-Item $PSScriptRoot).Parent.FullName
$BatPath = Join-Path $RootPath "DataMind.bat"
$WshShell = New-Object -ComObject WScript.Shell

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "   Data Mind - Windows Desktop Setup and Shortcuts" -ForegroundColor Cyan
Write-Host "   Think Data. Discover Intelligence." -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Desktop Shortcut
$DesktopDir = [Environment]::GetFolderPath("Desktop")
$DesktopShortcut = Join-Path $DesktopDir "Data Mind.lnk"
$Shortcut = $WshShell.CreateShortcut($DesktopShortcut)
$Shortcut.TargetPath = $BatPath
$Shortcut.WorkingDirectory = $RootPath
$Shortcut.Description = "Data Mind - Autonomous AI Data Analyst and Coding Agent"
$Shortcut.Save()
Write-Host "[OK] Desktop shortcut created at: $DesktopShortcut" -ForegroundColor Green

# 2. Start Menu Shortcut
$StartMenuDir = Join-Path ([Environment]::GetFolderPath("Programs")) "Data Mind"
if (-not (Test-Path $StartMenuDir)) {
    New-Item -ItemType Directory -Path $StartMenuDir | Out-Null
}
$StartMenuShortcut = Join-Path $StartMenuDir "Data Mind.lnk"
$Shortcut2 = $WshShell.CreateShortcut($StartMenuShortcut)
$Shortcut2.TargetPath = $BatPath
$Shortcut2.WorkingDirectory = $RootPath
$Shortcut2.Description = "Data Mind - Autonomous AI Data Analyst and Coding Agent"
$Shortcut2.Save()
Write-Host "[OK] Start Menu shortcut created at: $StartMenuShortcut" -ForegroundColor Green

Write-Host ""
Write-Host "Setup completed successfully! You can launch Data Mind directly from your Desktop or Start Menu." -ForegroundColor Cyan
