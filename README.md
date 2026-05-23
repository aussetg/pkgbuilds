# pkgbuilds

A small collection of AUR PKGBUILDs maintained in one repository.

## Packages

| Package | Type | Notes |
| --- | --- | --- |
| `arcana-git` | source (VCS) | Builds the latest `master` commit from `git.sr.ht/~aussetg/arcana` locally |
| `colgrep` | source | Built locally with host-native optimizations (`-march=native`, `-mtune=native`, Rust `target-cpu=native`) |
| `colgrep-bin` | binary | Installs the upstream prebuilt Linux x86_64 release |
| `obsidian-headless-bin` | npm binary | Installs the npm-published CLI and locally builds the `better-sqlite3` native addon |
| `pi-coding-agent-bin` | binary | Installs the upstream prebuilt Linux x86_64 release from `badlogic/pi-mono` |
| `migraphx-gfx1151` | source | Add-on package for `rocm-gfx1151-bin`; installs missing MIGraphX files without conflicting with the monolithic ROCm package |
| `mivisionx-gfx1151` | source | Add-on package for `rocm-gfx1151-bin`; installs missing MIVisionX files without conflicting with the monolithic ROCm package |
| `rpp-gfx1151` | source | Add-on package for `rocm-gfx1151-bin`; installs missing RPP files without conflicting with the monolithic ROCm package |
| `rocalution-gfx1151` | source | Add-on package for `rocm-gfx1151-bin`; installs missing rocALUTION files without conflicting with the monolithic ROCm package |
| `hiptensor-gfx1151` | source | Add-on package for `rocm-gfx1151-bin`; installs missing hipTensor files without conflicting with the monolithic ROCm package |
| `hipfort-gfx1151` | source | Add-on package for `rocm-gfx1151-bin`; installs missing hipfort files without conflicting with the monolithic ROCm package |

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

Automatic update tracking is enabled for:

- `colgrep`
- `colgrep-bin`
- `obsidian-headless-bin`
- `pi-coding-agent-bin`

## Required GitHub Actions secrets

- `AUR_USERNAME`
- `AUR_EMAIL`
- `AUR_SSH_PRIVATE_KEY`

The SSH key must have push access to the corresponding AUR repositories.

## Notes

- `colgrep` disables LTO because upstream currently fails to link correctly with distro LTO flags.
- `colgrep` is intentionally host-optimized and therefore should be built locally by each user.
- `colgrep-bin` is the generic alternative for users who want a prebuilt package.
- `obsidian-headless-bin` auto-updates are gated on npm metadata validation and a successful `makepkg` build because upstream bundles a native Node addon (`better-sqlite3`).
- `arcana-git` tracks the latest upstream commit and is intentionally excluded from the automated release update / AUR publish workflow.
- The `*-gfx1151` ROCm packages are local add-ons for the current `rocm-gfx1151-bin` package. They deliberately do not `provide` or `conflict` with the official ROCm component names because `rocm-gfx1151-bin` currently declares conflicts/provides for those names while not shipping the files.
