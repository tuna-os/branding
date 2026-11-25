#!/usr/bin/env python3
"""Regenerate and verify the digests in branding-manifest.json.

The manifest binds each asset to two SHA-256 digests:

``assets``
    Digest of the exact file bytes. Only a byte-for-byte copy matches it.

``canonical_assets``
    Digest of the file in XML Canonical form (C14N 2.0) with comments removed
    and leading/trailing whitespace stripped from text (``xml:space="preserve"``
    is honoured). A copy keeps this digest when it only adds or drops comments
    (for example an attribution header), changes the XML declaration, or is
    passed through a whitespace-stripping step such as GResource
    ``preprocess="xml-stripblanks"``. A changed element, attribute, colour,
    path or viewBox changes it.

Standard library only, so consumers can vendor this file next to the manifest.

Usage, from the root of this repository:

    python3 scripts/branding_manifest.py update

Usage, from a consumer that vendors copies of the marks:

    python3 branding_manifest.py verify --manifest branding-manifest.json \\
        marks/tunaos.svg=data/images/tunaos.svg ...
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from xml.etree.ElementTree import ParseError, canonicalize
from xml.parsers import expat

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_NAME = "branding-manifest.json"
ASSET_DIRS = ("marks", "wordmarks")


def file_digest(path: Path) -> str:
    """Return the ``sha256:`` digest of the exact bytes of ``path``."""
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical_digest(path: Path) -> str:
    """Return the ``sha256:`` digest of the canonical XML form of ``path``."""
    canonical = canonicalize(from_file=str(path), with_comments=False, strip_text=True)
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def has_doctype(path: Path) -> bool:
    """Return whether the XML in ``path`` has a ``<!DOCTYPE>`` declaration.

    This asks expat. ElementTree passes a DOCTYPE to its target, but without
    the C accelerator (``_elementtree``) it passes only a DOCTYPE that has an
    external identifier. A DOCTYPE with only an internal subset is not passed.
    """
    found = False

    def start_doctype(name, system, public, has_internal_subset):
        nonlocal found
        found = True

    parser = expat.ParserCreate()
    parser.StartDoctypeDeclHandler = start_doctype
    parser.Parse(Path(path).read_bytes(), True)
    return found


def asset_names(root: Path = ROOT) -> list[str]:
    """Return the repository-relative name of every asset SVG, sorted."""
    return sorted(
        path.relative_to(root).as_posix()
        for directory in ASSET_DIRS
        for path in (root / directory).glob("*.svg")
    )


def build_manifest(root: Path = ROOT) -> dict:
    """Return the manifest for the assets under ``root``.

    ``schema_version``, ``source`` and any other top-level keys are kept from
    the existing manifest; only the two digest maps are recomputed.
    """
    manifest = json.loads((root / MANIFEST_NAME).read_text(encoding="utf-8"))
    names = asset_names(root)
    manifest["assets"] = {name: file_digest(root / name) for name in names}
    manifest["canonical_assets"] = {name: canonical_digest(root / name) for name in names}
    return manifest


def render_manifest(manifest: dict) -> str:
    return json.dumps(manifest, indent=2) + "\n"


def verify_copy(manifest: dict, asset: str, copy: Path) -> tuple[bool, str]:
    """Check one vendored ``copy`` against manifest entry ``asset``.

    Returns ``(ok, detail)``. ``detail`` is ``"exact"`` or ``"canonical"`` on
    success, or the reason for the failure.
    """
    exact = manifest.get("assets", {})
    canonical = manifest.get("canonical_assets", {})
    if asset not in exact and asset not in canonical:
        return False, "not in manifest"
    if not Path(copy).is_file():
        return False, f"{copy} does not exist"
    if exact.get(asset) == file_digest(copy):
        return True, "exact"
    if asset in canonical:
        try:
            # Canonical form drops the DOCTYPE, which the contract suite forbids.
            if has_doctype(copy):
                return False, f"{copy} has a <!DOCTYPE> declaration"
            digest = canonical_digest(copy)
        except (ParseError, expat.ExpatError, ValueError) as error:
            return False, f"{copy} is not parseable XML: {error}"
        if canonical[asset] == digest:
            return True, "canonical"
    return False, "content differs from the manifest"


def _parse_pair(value: str) -> tuple[str, Path]:
    asset, separator, copy = value.partition("=")
    if not separator or not asset or not copy:
        raise argparse.ArgumentTypeError(f"expected ASSET=FILE, got {value!r}")
    return asset, Path(copy)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)

    update = commands.add_parser("update", help=f"rewrite {MANIFEST_NAME} from the SVG files")
    update.add_argument("--root", type=Path, default=ROOT, help="branding checkout")

    verify = commands.add_parser("verify", help="verify vendored copies against the manifest")
    verify.add_argument(
        "--manifest", type=Path, default=ROOT / MANIFEST_NAME, help="manifest to verify against"
    )
    verify.add_argument(
        "pairs", nargs="+", type=_parse_pair, metavar="ASSET=FILE",
        help="manifest asset name and the local copy of it",
    )

    args = parser.parse_args(argv)

    if args.command == "update":
        path = args.root / MANIFEST_NAME
        path.write_text(render_manifest(build_manifest(args.root)), encoding="utf-8")
        return 0

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    failed = False
    for asset, copy in args.pairs:
        ok, detail = verify_copy(manifest, asset, copy)
        print(f"{'ok' if ok else 'FAIL'}: {asset} = {copy} ({detail})")
        failed |= not ok
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
