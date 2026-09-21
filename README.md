# pkgbuilds

Locally maintained Arch Linux package recipes.

This repository contains a reviewed local baseline for every package currently
installed from the Arch User Repository (AUR), plus original packages maintained
here. The AUR baseline came from the local `paru` and `rua` snapshots that
produced the installed packages; it was not refreshed from the live AUR during
the migration.

## Packages

The complete migrated inventory is in [`aur-packages.txt`](aur-packages.txt).
See [`AUR-BASELINE.md`](AUR-BASELINE.md) for scope, provenance, exclusions, and
manual-source requirements.

Original packages maintained in this repository include:

| Package | Type | Notes |
| --- | --- | --- |
| `arcana-git` | source (VCS) | Builds the latest `master` commit from `git.sr.ht/~aussetg/arcana` locally |
| `bunny-cli-bin` | binary | Installs the upstream prebuilt bunny.net CLI for Linux x86_64/aarch64 |
| `colgrep` | source | Built locally with host-native optimizations (`-march=native`, `-mtune=native`, Rust `target-cpu=native`) |
| `colgrep-bin` | binary | Installs the upstream prebuilt Linux x86_64 release |
| `obsidian-headless-bin` | npm binary | Installs the npm-published CLI and locally builds the `better-sqlite3` native addon |
| `pi-coding-agent-bin` | binary | Installs the upstream prebuilt Linux x86_64 release from `badlogic/pi-mono` |
| `rocm-gfx1151-bin` | stable binary SDK | Installs AMD ROCm Core SDK 7.14 for gfx1151 with verified component metadata and repaired LLVM runtime files |
| `zoom` | binary | Repackages the official Zoom Workplace Arch tarball from the Zoom Download Center with Arch dependency mapping |
| `migraphx-gfx1151` | source | Installs the source-only MIGraphX 2.16.0 ROCm-Extras release for ROCm 7.14 with its exact pinned rocMLIR compiler |
| `opencarp` | source | Builds the openCARP 20.0 cardiac electrophysiology simulator against AUR PETSc; core simulator is non-commercial (APL-1.1) |
| `petsc` | source | PETSc 3.25.3 with a fixed all-[extra] dependency set (scotch, pastix, superlu_dist, zfp, hypre) instead of the AUR's build-time auto-detection; AUR-comment-informed |
| `carputils` | source | openCARP experiment framework pinned to the openCARP 20.0 submodule commit; ships a system default settings.yaml for this repo's layout |
| `meshtool` | source | Mesh manipulation tool, commit-pinned snapshot (upstream has no tags since 2019) with gzip, OpenMP and `-march=native` host tuning enabled |
| `meshalyzer` | source | openCARP OpenGL visualizer + headless `meglyzer` (EGL), commit-pinned snapshot; VTK support disabled |
| `hipfort-gfx1151` | source | Installs hipFORT 0.8.0 from its ROCm 7.14.0 source release with AMD Flang |

## Layout

Each package lives in its own directory and contains at least:

- `PKGBUILD`
- `.SRCINFO`

Some packages may also ship extra files such as patches.

## Updating locally

Regenerate `.SRCINFO` after changing a `PKGBUILD`:

```bash
cd <pkgname>
makepkg --printsrcinfo > .SRCINFO
```

Build locally:

```bash
cd <pkgname>
makepkg -fsc
```

Build from these local directories rather than asking an AUR helper to fetch a
recipe. Review each update against its upstream release before changing
`pkgver`, sources, or checksums.

Some proprietary packages require an installer downloaded through the vendor's
account or license flow. Put that exact file beside the package's `PKGBUILD`;
`makepkg` verifies its pinned checksum. See
[`AUR-BASELINE.md`](AUR-BASELINE.md#manual-sources).

## Automation

GitHub Actions checks `nvchecker.toml` for new upstream releases and, when updates are found:

1. updates the package version and checksums
2. regenerates `.SRCINFO`
3. pushes the package to the AUR
4. commits the updated packaging files and `old.json` back to this repository

Workflow file:

- `.github/workflows/update.yml`

Tracked versions are stored in:

- `old.json`

Automatic update tracking is currently enabled only for:

- `bunny-cli-bin`
- `colgrep`
- `colgrep-bin`
- `obsidian-headless-bin`
- `pi-coding-agent-bin`

The migrated inventory is intentionally not auto-updated from AUR.

## Required GitHub Actions secrets

- `AUR_USERNAME`
- `AUR_EMAIL`
- `AUR_SSH_PRIVATE_KEY`

The SSH key must have push access to the corresponding AUR repositories.

## Notes

- `colgrep` disables LTO because upstream currently fails to link correctly with distro LTO flags.
- `colgrep` is intentionally host-optimized and therefore should be built locally by each user.
- `meshtool` is likewise host-optimized (`-march=native`, upstream `TUNE_NATIVE`) and should be built locally by each user.
- `colgrep-bin` is the generic alternative for users who want a prebuilt package.
- `obsidian-headless-bin` auto-updates are gated on npm metadata validation and a successful `makepkg` build because upstream bundles a native Node addon (`better-sqlite3`).
- `arcana-git` tracks the latest upstream commit and is intentionally excluded from the automated release update / AUR publish workflow.
- `rocm-gfx1151-bin` advertises only components verified in AMD's stable 7.14
  payload. MIGraphX and hipFORT have matching, separate source packages.
  AMD lists RPP and MIVisionX as planned for future 7.14 releases, so stale
  7.2/7.13 recipes were removed and neither name is provided. hipTensor and
  rocALUTION are already included in the Core SDK. See
  `rocm-gfx1151-bin/ROCM-COMPONENTS.md`.
