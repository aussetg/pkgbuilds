#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "usage: $0 <package-dir>" >&2
  exit 1
fi

pkgdir=$1
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
repo_root=$(cd -- "${script_dir}/../.." && pwd -P)

if [[ $(id -u) -eq 0 ]] && id builder >/dev/null 2>&1; then
  chown -R builder:builder "${repo_root}/${pkgdir}"
fi

run_cmd() {
  local cmd=$1
  if [[ $(id -u) -eq 0 ]] && id builder >/dev/null 2>&1; then
    sudo -u builder bash -lc "$cmd"
  else
    bash -lc "$cmd"
  fi
}

case "$pkgdir" in
  obsidian-headless-bin)
    run_cmd "cd '${repo_root}/${pkgdir}' && makepkg -fsc --noconfirm"
    rm -f "${repo_root}/${pkgdir}"/*.pkg.tar.* "${repo_root}/${pkgdir}"/*.src.tar.* "${repo_root}/${pkgdir}"/*.tgz
    ;;
  *)
    echo "No extra validation configured for ${pkgdir}"
    ;;
esac
