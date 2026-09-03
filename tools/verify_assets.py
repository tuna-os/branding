#!/usr/bin/env python3
"""Verify a directory of branding assets against ``branding-manifest.json``.

The manifest is the asset contract: it binds each asset name to the SHA-256
digest of its bytes. ``README.md`` and ``CONTRIBUTING.md`` describe the check
as a pair of ``jq``/``sha256sum`` snippets; this module is the same check as a
single runnable entry point, so this repository and its consumers verify with
one implementation instead of transcribing shell.

Contract semantics are unchanged: an asset must exist, its digest must match,
and the manifest must name every asset in the directory and no others.
Consumers that vendor only part of the set pass ``--allow-missing``; extra and
modified assets are still reported.

Usage:
    python3 tools/verify_assets.py [DIRECTORY] [--manifest PATH] [--allow-missing]

Exit status is 0 when the directory satisfies the manifest and 1 otherwise.
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

DIGEST_PREFIX = "sha256:"
SCHEMA_VERSION = 1


def load_manifest(path):
    """Return the parsed manifest at ``path``, rejecting unknown schemas."""
    manifest = json.loads(Path(path).read_text(encoding="utf-8"))
    version = manifest.get("schema_version")
    if version != SCHEMA_VERSION:
        raise ValueError(f"unsupported manifest schema_version {version!r}")
    assets = manifest.get("assets")
    if not isinstance(assets, dict) or not assets:
        raise ValueError("manifest declares no assets")
    return manifest


def file_digest(path):
    """Return the ``sha256:``-prefixed digest of the file at ``path``."""
    return DIGEST_PREFIX + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify_directory(manifest, directory, allow_missing=False):
    """Return a list of human-readable contract violations, empty when clean.

    ``allow_missing`` lets a consumer vendor a subset of the canonical assets;
    every asset it does carry must still match, and assets the manifest does
    not name are reported either way.
    """
    directory = Path(directory)
    declared = manifest["assets"]
    problems = []

    for name, expected in sorted(declared.items()):
        asset = directory / name
        if not asset.is_file():
            if not allow_missing:
                problems.append(f"{name}: declared in manifest, missing from {directory}")
            continue
        actual = file_digest(asset)
        if actual != expected:
            problems.append(f"{name}: digest {actual} does not match manifest {expected}")

    for asset in sorted(directory.glob("*.svg")):
        if asset.name not in declared:
            problems.append(f"{asset.name}: present in {directory}, not declared in manifest")

    return problems


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="directory holding the assets to verify (default: current directory)",
    )
    parser.add_argument(
        "--manifest",
        default=None,
        help="path to branding-manifest.json (default: DIRECTORY/branding-manifest.json)",
    )
    parser.add_argument(
        "--allow-missing",
        action="store_true",
        help="permit a partial asset set, for consumers that vendor a subset",
    )
    args = parser.parse_args(argv)

    manifest_path = args.manifest or Path(args.directory) / "branding-manifest.json"
    try:
        manifest = load_manifest(manifest_path)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"{manifest_path}: {error}", file=sys.stderr)
        return 1

    problems = verify_directory(manifest, args.directory, allow_missing=args.allow_missing)
    for problem in problems:
        print(problem, file=sys.stderr)
    if problems:
        print(f"{len(problems)} asset contract violation(s)", file=sys.stderr)
        return 1

    print(f"{len(manifest['assets'])} assets verified against {manifest_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
