# pkgbuilds

A small collection of AUR PKGBUILDs maintained in one repository.

## Packages

| Package | Type | Notes |
| --- | --- | --- |
| `colgrep` | source | Built locally with host-native optimizations (`-march=native`, `-mtune=native`, Rust `target-cpu=native`) |
| `colgrep-bin` | binary | Installs the upstream prebuilt Linux x86_64 release |
| `pi-coding-agent-bin` | binary | Installs the upstream prebuilt Linux x86_64 release from `badlogic/pi-mono` |

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
