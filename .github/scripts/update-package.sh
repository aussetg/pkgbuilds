#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "usage: $0 <package-dir> <new-version>" >&2
  exit 1
fi

pkgdir=$1
newver=$2
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
repo_root=$(cd -- "${script_dir}/../.." && pwd -P)
pkgpath="${repo_root}/${pkgdir}"

if [[ ! -f "$pkgpath/PKGBUILD" ]]; then
  echo "PKGBUILD not found: $pkgpath/PKGBUILD" >&2
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
  chown -R builder:builder "$pkgpath"
fi

updater_py="${script_dir}/update-${pkgdir}.py"
updater_sh="${script_dir}/update-${pkgdir}.sh"

if [[ -f "$updater_py" ]]; then
  python "$updater_py" "$pkgpath" "$newver"
elif [[ -f "$updater_sh" ]]; then
  bash "$updater_sh" "$pkgpath" "$newver"
else
  cd "$pkgpath"
  sed -i "s/^pkgver=.*/pkgver=$newver/" PKGBUILD
  sed -i "s/^pkgrel=.*/pkgrel=1/" PKGBUILD
fi

cd "$pkgpath"

run_cmd "cd '$PWD' && updpkgsums"
run_cmd "cd '$PWD' && makepkg --printsrcinfo > .SRCINFO"
