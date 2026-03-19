#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "usage: $0 <package-dir> <new-version>" >&2
  exit 1
fi

pkgdir=$1
newver=$2

if [[ ! -f "$pkgdir/PKGBUILD" ]]; then
  echo "PKGBUILD not found: $pkgdir/PKGBUILD" >&2
  exit 1
fi

run_cmd() {
  local cmd=$1
  if [[ $(id -u) -eq 0 ]] && id builder >/dev/null 2>&1; then
    sudo -u builder bash -lc "$cmd"
  else
    bash -lc "$cmd"
  fi
}

if [[ $(id -u) -eq 0 ]] && id builder >/dev/null 2>&1; then
  chown -R builder:builder "$pkgdir"
fi

cd "$pkgdir"

sed -i "s/^pkgver=.*/pkgver=$newver/" PKGBUILD
sed -i "s/^pkgrel=.*/pkgrel=1/" PKGBUILD

run_cmd "cd '$PWD' && updpkgsums"
run_cmd "cd '$PWD' && makepkg --printsrcinfo > .SRCINFO"
