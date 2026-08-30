#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
version="${1:-1.0.0}"
cd "$project_dir"

python_bin="${PYTHON_BIN:-$project_dir/.venv/bin/python}"
if ! command -v "$python_bin" >/dev/null 2>&1 && [[ ! -x "$python_bin" ]]; then
  python3 -m venv .venv
  python_bin="$project_dir/.venv/bin/python"
fi
"$python_bin" -m pip install -r requirements-build.txt
"$python_bin" -m PyInstaller \
  --noconfirm --clean --windowed --name SlideShower \
  --osx-bundle-identifier se.slideshower.app \
  --collect-all pillow_heif slideshow.py

mkdir -p installers
hdiutil create \
  -volname SlideShower \
  -srcfolder dist/SlideShower.app \
  -ov -format UDZO \
  "installers/SlideShower-${version}-macOS.dmg"
