#!/usr/bin/env python3

import json
import re
import subprocess
import sys
from pathlib import Path


EXPECTED_OBSIDIAN_DEPS = {"better-sqlite3", "commander"}
EXPECTED_BIN = {"ob": "cli.js"}
EXPECTED_CPU = {"x64", "arm64"}
EXPECTED_BETTER_SQLITE3_DEPS = {"bindings", "prebuild-install"}
EXPECTED_BINDINGS_DEPS = {"file-uri-to-path"}


class UpdateError(RuntimeError):
    pass


def npm_view(selector: str, *fields: str):
    cmd = ["npm", "view", selector]
    cmd.extend(fields)
    cmd.append("--json")
    proc = subprocess.run(cmd, check=True, capture_output=True, text=True)
    data = proc.stdout.strip()
    if not data:
        raise UpdateError(f"npm view returned no data for {selector}")
    return json.loads(data)


def pick_latest(value, *, selector: str, field: str):
    if isinstance(value, list):
        if not value:
            raise UpdateError(f"npm view returned an empty list for {selector} {field}")
        return value[-1]
    return value


def resolve_version(name: str, spec: str) -> str:
    value = npm_view(f"{name}@{spec}", "version")
    value = pick_latest(value, selector=f"{name}@{spec}", field="version")
    if not isinstance(value, str) or not value:
        raise UpdateError(f"could not resolve a concrete version for {name}@{spec}")
    return value


def get_package_meta(name: str, version: str) -> dict:
    value = npm_view(f"{name}@{version}")
    value = pick_latest(value, selector=f"{name}@{version}", field="<all>")
    if not isinstance(value, dict):
        raise UpdateError(f"unexpected metadata shape for {name}@{version}: {type(value).__name__}")
    return value


def deps_map(value) -> dict:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise UpdateError(f"expected a dependency mapping, got {type(value).__name__}")
    return value


def assert_true(condition: bool, message: str):
    if not condition:
        raise UpdateError(message)


def assert_keys(mapping: dict, expected: set[str], label: str):
    actual = set(mapping)
    if actual != expected:
        raise UpdateError(
            f"{label} changed from {sorted(expected)} to {sorted(actual)}; manual review required"
        )


def parse_node_engine(spec: str) -> str:
    if not isinstance(spec, str):
        raise UpdateError("obsidian-headless engines.node is missing; manual review required")
    match = re.fullmatch(r"\s*>=\s*([0-9]+)(?:\.\d+\.\d+)?\s*", spec)
    if not match:
        raise UpdateError(
            f"unsupported engines.node value {spec!r}; manual review required"
        )
    return match.group(1)


def replace_once(text: str, pattern: str, replacement: str, label: str) -> str:
    updated, count = re.subn(pattern, replacement, text, flags=re.MULTILINE)
    if count != 1:
        raise UpdateError(f"failed to update {label} in PKGBUILD")
    return updated


def main() -> int:
    if len(sys.argv) != 3:
        print(
            f"usage: {Path(sys.argv[0]).name} <package-dir> <new-version>",
            file=sys.stderr,
        )
        return 1

    pkgdir = Path(sys.argv[1])
    new_version = sys.argv[2]
    pkgbuild_path = pkgdir / "PKGBUILD"

    if not pkgbuild_path.is_file():
        raise UpdateError(f"PKGBUILD not found: {pkgbuild_path}")

    obsidian = get_package_meta("obsidian-headless", new_version)

    assert_true(
        obsidian.get("name") == "obsidian-headless",
        "unexpected upstream package name for obsidian-headless",
    )
    assert_true(
        obsidian.get("version") == new_version,
        f"npm metadata returned version {obsidian.get('version')!r} instead of {new_version!r}",
    )
    assert_true(
        obsidian.get("license") == "UNLICENSED",
        "obsidian-headless license changed; manual review required",
    )
    assert_true(
        obsidian.get("bin") == EXPECTED_BIN,
        f"obsidian-headless bin changed from {EXPECTED_BIN!r}; manual review required",
    )

    obsidian_deps = deps_map(obsidian.get("dependencies"))
    assert_keys(obsidian_deps, EXPECTED_OBSIDIAN_DEPS, "obsidian-headless dependencies")
    assert_true(
        not deps_map(obsidian.get("optionalDependencies")),
        "obsidian-headless optionalDependencies changed; manual review required",
    )
    assert_true(
        not deps_map(obsidian.get("peerDependencies")),
        "obsidian-headless peerDependencies changed; manual review required",
    )
    assert_true(
        "linux" in set(obsidian.get("os") or []),
        "obsidian-headless no longer supports Linux; manual review required",
    )
    actual_cpu = set(obsidian.get("cpu") or [])
    assert_true(
        actual_cpu == EXPECTED_CPU,
        f"obsidian-headless cpu list changed from {sorted(EXPECTED_CPU)} to {sorted(actual_cpu)}; manual review required",
    )

    node_major = parse_node_engine(deps_map(obsidian.get("engines")).get("node"))

    commander_version = resolve_version("commander", obsidian_deps["commander"])
    commander = get_package_meta("commander", commander_version)
    assert_true(
        not deps_map(commander.get("dependencies")),
        "commander gained dependencies; manual review required",
    )
    assert_true(
        not deps_map(commander.get("optionalDependencies")),
        "commander gained optionalDependencies; manual review required",
    )
    assert_true(
        not deps_map(commander.get("peerDependencies")),
        "commander gained peerDependencies; manual review required",
    )

    better_sqlite3_version = resolve_version("better-sqlite3", obsidian_deps["better-sqlite3"])
    better_sqlite3 = get_package_meta("better-sqlite3", better_sqlite3_version)
    better_sqlite3_deps = deps_map(better_sqlite3.get("dependencies"))
    assert_keys(
        better_sqlite3_deps,
        EXPECTED_BETTER_SQLITE3_DEPS,
        "better-sqlite3 dependencies",
    )
    assert_true(
        not deps_map(better_sqlite3.get("optionalDependencies")),
        "better-sqlite3 optionalDependencies changed; manual review required",
    )
    assert_true(
        not deps_map(better_sqlite3.get("peerDependencies")),
        "better-sqlite3 peerDependencies changed; manual review required",
    )
    install_script = deps_map(better_sqlite3.get("scripts")).get("install", "")
    assert_true(
        isinstance(install_script, str) and "node-gyp rebuild" in install_script,
        "better-sqlite3 install/build flow changed; manual review required",
    )

    bindings_version = resolve_version("bindings", better_sqlite3_deps["bindings"])
    bindings = get_package_meta("bindings", bindings_version)
    bindings_deps = deps_map(bindings.get("dependencies"))
    assert_keys(bindings_deps, EXPECTED_BINDINGS_DEPS, "bindings dependencies")
    assert_true(
        not deps_map(bindings.get("optionalDependencies")),
        "bindings optionalDependencies changed; manual review required",
    )
    assert_true(
        not deps_map(bindings.get("peerDependencies")),
        "bindings peerDependencies changed; manual review required",
    )

    file_uri_to_path_version = resolve_version(
        "file-uri-to-path", bindings_deps["file-uri-to-path"]
    )
    file_uri_to_path = get_package_meta("file-uri-to-path", file_uri_to_path_version)
    assert_true(
        not deps_map(file_uri_to_path.get("dependencies")),
        "file-uri-to-path gained dependencies; manual review required",
    )
    assert_true(
        not deps_map(file_uri_to_path.get("optionalDependencies")),
        "file-uri-to-path gained optionalDependencies; manual review required",
    )
    assert_true(
        not deps_map(file_uri_to_path.get("peerDependencies")),
        "file-uri-to-path gained peerDependencies; manual review required",
    )

    pkgbuild = pkgbuild_path.read_text()
    pkgbuild = replace_once(pkgbuild, r"^pkgver=.*$", f"pkgver={new_version}", "pkgver")
    pkgbuild = replace_once(pkgbuild, r"^pkgrel=.*$", "pkgrel=1", "pkgrel")
    pkgbuild = replace_once(
        pkgbuild,
        r"^depends=\('gcc-libs' 'nodejs>=\d+'\)$",
        f"depends=('gcc-libs' 'nodejs>={node_major}')",
        "depends",
    )
    pkgbuild = replace_once(
        pkgbuild,
        r"^_better_sqlite3_ver=.*$",
        f"_better_sqlite3_ver={better_sqlite3_version}",
        "_better_sqlite3_ver",
    )
    pkgbuild = replace_once(
        pkgbuild,
        r"^_commander_ver=.*$",
        f"_commander_ver={commander_version}",
        "_commander_ver",
    )
    pkgbuild = replace_once(
        pkgbuild,
        r"^_bindings_ver=.*$",
        f"_bindings_ver={bindings_version}",
        "_bindings_ver",
    )
    pkgbuild = replace_once(
        pkgbuild,
        r"^_file_uri_to_path_ver=.*$",
        f"_file_uri_to_path_ver={file_uri_to_path_version}",
        "_file_uri_to_path_ver",
    )

    pkgbuild_path.write_text(pkgbuild)

    print(
        "Validated obsidian-headless-bin update:",
        f"pkgver={new_version}",
        f"nodejs>={node_major}",
        f"better-sqlite3={better_sqlite3_version}",
        f"commander={commander_version}",
        f"bindings={bindings_version}",
        f"file-uri-to-path={file_uri_to_path_version}",
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except UpdateError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
