param([string]$Version = "1.0.0")
$ErrorActionPreference = "Stop"
$ProjectDir = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectDir

if (-not (Test-Path ".venv")) { py -m venv .venv }
& .venv\Scripts\python -m pip install -r requirements-build.txt
& .venv\Scripts\python -m PyInstaller --noconfirm --clean --windowed `
  --name SlideShower --collect-all pillow_heif slideshow.py

$Iscc = Get-Command iscc.exe -ErrorAction SilentlyContinue
if (-not $Iscc) {
  throw "Inno Setup 6 saknas. Installera det och kör skriptet igen."
}
& $Iscc.Source "/DMyAppVersion=$Version" "packaging\windows-installer.iss"
