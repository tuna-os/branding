#!/usr/bin/env python3
"""Check marks/ and wordmarks/ against their tuna-os/tunaOS sources.

NOTICE says each SVG here is a byte copy of a tunaOS file:

    marks/<variant>.svg          <- system_files/usr/share/tunaos/logos/<variant>.svg
    marks/tunaos.svg             <- system_files/usr/share/pixmaps/tunaos.svg
    wordmarks/<variant>[-dark].svg
                                 <- system_files/usr/share/tunaos/lettermarks/<variant>[-dark].svg

This script makes that mapping executable. It reports each copy that is
missing, extra, or different from its source, and exits 1 if there is any.
Standard library only. It needs a local tunaOS checkout and no network.

Usage, from the root of this repository:

    python3 scripts/check_upstream.py /path/to/tunaOS
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# (copy directory here, source directory in tunaOS). Every *.svg in the source
# directory maps to the same file name in the copy directory.
DIRECTORY_MAP = (
    ("marks", "system_files/usr/share/tunaos/logos"),
    ("wordmarks", "system_files/usr/share/tunaos/lettermarks"),
)
# Single-file mappings that override the directory map.
FILE_MAP = {"marks/tunaos.svg": "system_files/usr/share/pixmaps/tunaos.svg"}


def expected_sources(upstream: Path) -> dict[str, Path]:
    """Return {copy path relative to this repo: source path} for a tunaOS tree."""
    sources: dict[str, Path] = {}
    for copy_dir, source_dir in DIRECTORY_MAP:
        directory = upstream / source_dir
        if directory.is_dir():
            for path in sorted(directory.glob("*.svg")):
                sources[f"{copy_dir}/{path.name}"] = path
    for copy, source in FILE_MAP.items():
        sources[copy] = upstream / source
    return sources


def local_copies(root: Path) -> set[str]:
    return {
        f"{copy_dir}/{path.name}"
        for copy_dir, _ in DIRECTORY_MAP
        if (root / copy_dir).is_dir()
        for path in (root / copy_dir).glob("*.svg")
    }


def check(upstream: Path, root: Path = ROOT) -> list[str]:
    """Return one message per missing, extra or differing copy. Empty means in sync."""
    problems = []
    sources = expected_sources(upstream)
    copies = local_copies(root)
    for copy, source in sources.items():
        if not source.is_file():
            if copy in copies:
                problems.append(f"extra: {copy} has no source at {source.relative_to(upstream)}")
        elif copy not in copies:
            problems.append(f"missing: {copy} (source {source.relative_to(upstream)})")
        elif (root / copy).read_bytes() != source.read_bytes():
            problems.append(f"differs: {copy} (source {source.relative_to(upstream)})")
    for copy in sorted(copies - set(sources)):
        problems.append(f"extra: {copy} has no source in the tunaOS checkout")
    return sorted(problems)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("upstream", type=Path, help="path to a tuna-os/tunaOS checkout")
    args = parser.parse_args(argv)
    if not (args.upstream / "system_files").is_dir():
        print(f"error: {args.upstream} has no system_files/, not a tunaOS checkout", file=sys.stderr)
        return 2
    problems = check(args.upstream)
    for problem in problems:
        print(problem)
    if problems:
        print(f"{len(problems)} copy(ies) out of sync with tunaOS", file=sys.stderr)
        return 1
    print("marks/ and wordmarks/ match tunaOS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
