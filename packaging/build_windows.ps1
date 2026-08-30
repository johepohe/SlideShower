param([string]$Version = "1.0.0")
$ErrorActionPreference = "Stop"
$ProjectDir = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectDir

if (-not (Test-Path ".venv")) { python -m venv .venv }
& .venv\Scripts\python -m pip install -r requirements-build.txt
& .venv\Scripts\python -m PyInstaller --noconfirm --clean --windowed `
  --name SlideShower --collect-all pillow_heif slideshow.py

$Iscc = Get-Command iscc.exe -ErrorAction SilentlyContinue
if (-not $Iscc) {
  $KnownIscc = "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe"
  if (Test-Path $KnownIscc) {
    $Iscc = Get-Item $KnownIscc
  } else {
    throw "Inno Setup 6 saknas. Installera det och kör skriptet igen."
  }
}
$IsccPath = if ($Iscc.Path) { $Iscc.Path } else { $Iscc.FullName }
& $IsccPath "/DMyAppVersion=$Version" "packaging\windows-installer.iss"
