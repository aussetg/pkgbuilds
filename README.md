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
| `fframes` | source | Builds the `cargo-fframes` video project generator; renderers compile inside each generated project |
| `frida-server-bin` | binary | Installs the upstream prebuilt `frida-server` for root-level instrumentation of the local system |
| `frida-core` | source | Builds `libfrida-core` (QuickJS backend) at the exact version pinned by Luma's upstream CI; consumed by `luma-bin` in place of the frida runtime bundled in upstream's .deb. Version is coupled to Luma's release pins, not latest frida |
| `luma-bin` | binary (hybrid) | The official Frida GUI from upstream's Ubuntu 26.04 build, minus its bundled frida runtime (provided by `frida-core` instead); only the Swift runtime stays bundled, as Arch has no system Swift. A full source build is parked until upstream's next release, which replaces the gir2swift bindings stack that cannot handle current GTK/HarfBuzz/radare2 |
| `swift-bin` | binary | Rolling swift.org toolchain (latest stable Swift, Ubuntu 24.04 build) under `/opt/swift-<major.minor>`; owns the interactive PATH default. Pinned toolchains install beside it |
| `swift-6.2-bin` | binary | Swift 6.2 toolchain from swift.org, pinned to Luma's upstream `SWIFT_VERSION`; currently unconsumed after the Luma source build was parked — kept for the next upstream release, whose new bindings architecture may make source builds viable |
| `frida-tools` | source (Python sdist) | Frida CLI tools (`frida`, `frida-trace`, `frida-ps`, …) built from the PyPI sdist, which ships the prebuilt REPL/tracer agents |
| `python-frida-bin` | binary (Python wheel) | Installs the official PyPI wheels of the `frida` Python bindings, which bundle the frida-core runtime |
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
| `mlir` | source | MLIR 22.1.8 built against system LLVM 22 with Python (nanobind) bindings installed into the system interpreter's site-packages; carries the upstream nanobind 3 compile fix plus a multi-DSO runtime fix |
| `rr` | source | Record-and-replay debugger 5.9.0; carries the termio build fix and the upstream Strix Halo (Zen 5) CPU-id backport, both already on master. check() record/replay smoke test skips when perf_event_open is denied by kernel policy or the host's CrowdStrike Falcon agent |

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

Check and apply upstream updates across the whole repository with
[`update-all.py`](update-all.py) (Python 3.11+, no third-party dependencies). It
refreshes upstream versions through nvchecker and reports, per package:

- recipes that lag their upstream version (`upstream -> recipe`), and
- recipes that are newer than the locally installed package
  (`installed -> recipe`) — rebuild those with `cd <pkgname> && makepkg -sirc`
  to apply the update to this system.

```bash
./update-all.py --status   # three-way report: upstream / recipe / installed
./update-all.py            # report, then bump outdated recipes
./update-all.py --commit   # … and git commit the bumps
./update-all.py pkg…       # limit to named packages
```

`--init` reseeds `old.json` after adding packages, `--take pkg` acknowledges a
manually bumped version, `--json` emits a machine-readable report, and
`--no-fetch` reuses the existing `new.json` offline. nvchecker runs via `uvx`
when not installed natively; a GitHub token is read from `keyfile.toml`
(seeded from `NVCHECKER_GITHUB_TOKEN`).

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
