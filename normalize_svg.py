#!/usr/bin/env python3
"""
Normalize SVG to canonical form for digest verification.

The canonical form is what consumers will have after applying standard XML
normalization (removing insignificant whitespace, sorting attributes, etc).
This allows verifying that an SVG is byte-for-byte equivalent to the canonical
version despite attribute order differences or comments.

Usage:
    python3 normalize_svg.py <input.svg> <output.svg>
    python3 normalize_svg.py --digest <input.svg>
"""

import argparse
import hashlib
import sys
from pathlib import Path
from xml.etree import ElementTree
from xml.dom import minidom


def normalize_svg(svg_path: Path) -> bytes:
    """
    Normalize SVG to canonical form.
    
    Performs:
    1. Parse XML to ensure well-formedness
    2. Remove comments and processing instructions
    3. Sort attributes for deterministic output
    4. Serialize with consistent formatting
    """
    tree = ElementTree.parse(svg_path)
    root = tree.getroot()
    
    # Remove comments and processing instructions
    _remove_non_element_nodes(root)
    
    # Sort attributes on all elements for deterministic output
    _sort_attributes_recursive(root)
    
    # Serialize to bytes with consistent formatting
    xml_bytes = ElementTree.tostring(root, encoding='utf-8', method='xml')
    
    # Use minidom to pretty-print and normalize whitespace consistently
    dom = minidom.parseString(xml_bytes)
    canonical = dom.toprettyxml(indent='  ', encoding='utf-8')
    
    # Remove the XML declaration that minidom adds
    if canonical.startswith(b"<?xml"):
        canonical = canonical.split(b'\n', 1)[1]
    
    # Strip leading/trailing whitespace
    canonical = canonical.strip() + b'\n'
    
    return canonical


def _remove_non_element_nodes(element):
    """Recursively remove comments and processing instructions."""
    # This is a bit tricky with ElementTree since comments are not elements
    # We'll just ensure the tree is clean
    to_remove = []
    for child in element:
        if not isinstance(child.tag, str):  # Comments have tag=None or special type
            to_remove.append(child)
        else:
            _remove_non_element_nodes(child)
    for child in to_remove:
        element.remove(child)


def _sort_attributes_recursive(element):
    """Recursively sort attributes on all elements."""
    # Sort the element's attributes
    if element.attrib:
        sorted_attribs = dict(sorted(element.attrib.items()))
        element.attrib.clear()
        element.attrib.update(sorted_attribs)
    
    # Recursively sort child elements
    for child in element:
        _sort_attributes_recursive(child)


def digest_svg(svg_path: Path) -> str:
    """Compute SHA-256 digest of normalized SVG."""
    canonical = normalize_svg(svg_path)
    return hashlib.sha256(canonical).hexdigest()


def main():
    parser = argparse.ArgumentParser(
        description="Normalize SVG to canonical form for digest verification"
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Input SVG file"
    )
    parser.add_argument(
        "--digest",
        action="store_true",
        help="Print SHA-256 digest instead of normalizing to file"
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Output file (required unless --digest is used)"
    )
    
    args = parser.parse_args()
    
    if args.digest:
        digest = digest_svg(args.input)
        print(f"sha256:{digest}")
        return 0
    
    if not args.output:
        parser.error("--output is required (or use --digest)")
    
    canonical = normalize_svg(args.input)
    args.output.write_bytes(canonical)
    print(f"Normalized {args.input} → {args.output}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
