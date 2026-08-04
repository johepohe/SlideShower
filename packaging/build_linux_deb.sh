#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
version="${1:-1.0.0}"
architecture="$(dpkg --print-architecture)"
package_dir="$project_dir/build/deb-root"
output_dir="$project_dir/installers"

cd "$project_dir"
python_bin="${PYTHON_BIN:-$project_dir/.venv/bin/python}"

"$python_bin" -m PyInstaller \
  --noconfirm \
  --clean \
  --windowed \
  --name SlideShower \
  --collect-all pillow_heif \
  slideshow.py

rm -rf -- "$package_dir"
mkdir -p \
  "$package_dir/DEBIAN" \
  "$package_dir/opt/slideshower" \
  "$package_dir/usr/bin" \
  "$package_dir/usr/share/applications" \
  "$package_dir/usr/share/icons/hicolor/scalable/apps" \
  "$output_dir"

cp -a dist/SlideShower/. "$package_dir/opt/slideshower/"
install -m 0755 packaging/linux-launcher "$package_dir/usr/bin/slideshower"
install -m 0644 packaging/slideshower.desktop \
  "$package_dir/usr/share/applications/slideshower.desktop"
install -m 0644 packaging/slideshower.svg \
  "$package_dir/usr/share/icons/hicolor/scalable/apps/slideshower.svg"

installed_size="$(du -sk "$package_dir/opt/slideshower" | cut -f1)"
cat > "$package_dir/DEBIAN/control" <<EOF
Package: slideshower
Version: $version
Section: graphics
Priority: optional
Architecture: $architecture
Installed-Size: $installed_size
Maintainer: SlideShower
Depends: libc6, libx11-6, libxcb1, libxcb-cursor0, libxkbcommon-x11-0
Description: Fullskärmsbildspel sorterat efter fotograferingsdatum
 SlideShower läser JPG-, JPEG-, HEIC- och HEIF-bilder rekursivt och
 visar dem i EXIF-datumordning.
EOF

dpkg-deb --root-owner-group --build "$package_dir" \
  "$output_dir/slideshower_${version}_${architecture}.deb"
echo "Skapad: $output_dir/slideshower_${version}_${architecture}.deb"
