#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "usage: $0 <package-dir> <new-version>" >&2
  exit 1
fi

pkgdir=$1
newver=$2
if [[ -z "$newver" || "$newver" =~ [[:space:]:/-] ]]; then
  echo "invalid pkgver: $newver" >&2
  exit 1
fi

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

# Keep the recipe and its metadata in sync if an updater or download fails.
backup_dir=$(mktemp -d)
cp -p -- "$pkgpath/PKGBUILD" "$backup_dir/PKGBUILD"
if [[ -f "$pkgpath/.SRCINFO" ]]; then
  cp -p -- "$pkgpath/.SRCINFO" "$backup_dir/.SRCINFO"
fi

finish() {
  local status=$?
  if (( status != 0 )); then
    cp -p -- "$backup_dir/PKGBUILD" "$pkgpath/PKGBUILD"
    if [[ -f "$backup_dir/.SRCINFO" ]]; then
      cp -p -- "$backup_dir/.SRCINFO" "$pkgpath/.SRCINFO"
    else
      rm -f -- "$pkgpath/.SRCINFO"
    fi
  fi
  rm -rf -- "$backup_dir"
  exit "$status"
}
trap finish EXIT

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
