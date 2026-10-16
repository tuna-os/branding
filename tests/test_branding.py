import hashlib
import json
import subprocess
import unittest
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "branding-manifest.json"
SVG_NAMESPACE = "http://www.w3.org/2000/svg"
XLINK_HREF = "{http://www.w3.org/1999/xlink}href"


def canonical_digest(svg_path: Path) -> str:
    """Compute canonical form digest using the normalizer script."""
    normalizer = ROOT / "normalize_svg.py"
    result = subprocess.run(
        ["python3", str(normalizer), "--digest", str(svg_path)],
        capture_output=True,
        text=True,
        check=True
    )
    return result.stdout.strip()


class BrandingContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    def test_manifest_schema(self):
        self.assertEqual(self.manifest["schema_version"], 2)
        self.assertEqual(self.manifest["source"], "https://github.com/tuna-os/branding")
        self.assertIn("revision", self.manifest)
        self.assertIsInstance(self.manifest["assets"], dict)
        self.assertTrue(self.manifest["assets"])
        # Validate revision is a commit hash (40 hex chars for SHA-1)
        revision = self.manifest["revision"]
        self.assertEqual(len(revision), 40, "revision should be a full commit hash")
        self.assertTrue(all(c in "0123456789abcdef" for c in revision), "revision should be hex")

    def test_manifest_contains_every_and_only_root_svg(self):
        files = {path.name for path in ROOT.glob("*.svg")}
        self.assertEqual(set(self.manifest["assets"]), files)
    
    def test_asset_entries_have_both_digest_types(self):
        """Each asset must declare both canonical and raw-byte digests."""
        for name, entry in self.manifest["assets"].items():
            with self.subTest(asset=name):
                self.assertIn("canonical_sha256", entry, f"{name} missing canonical_sha256")
                self.assertIn("bytes_sha256", entry, f"{name} missing bytes_sha256")

    def test_asset_bytes_digests_match_manifest(self):
        """Verify raw-file SHA-256 digests (legacy compatibility)."""
        for name, entry in self.manifest["assets"].items():
            with self.subTest(asset=name):
                digest = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                self.assertEqual(entry["bytes_sha256"], f"sha256:{digest}")
    
    def test_asset_canonical_digests_match_manifest(self):
        """Verify canonical-form digests (normalized for comparison)."""
        for name, entry in self.manifest["assets"].items():
            with self.subTest(asset=name):
                digest = canonical_digest(ROOT / name)
                self.assertEqual(entry["canonical_sha256"], digest)

    def test_assets_are_parseable_128_square_svgs(self):
        for name in self.manifest["assets"]:
            with self.subTest(asset=name):
                root = ElementTree.parse(ROOT / name).getroot()
                self.assertEqual(root.tag, f"{{{SVG_NAMESPACE}}}svg")
                self.assertEqual(root.attrib.get("viewBox"), "0 0 128 128")

    def test_assets_have_no_external_references(self):
        for name in self.manifest["assets"]:
            with self.subTest(asset=name):
                root = ElementTree.parse(ROOT / name).getroot()
                for element in root.iter():
                    for attribute in ("href", XLINK_HREF):
                        reference = element.attrib.get(attribute)
                        if reference is not None:
                            self.assertTrue(
                                reference.startswith("#"),
                                f"{name} has external reference {reference!r}",
                            )
                    for value in element.attrib.values():
                        self.assertNotRegex(
                            value,
                            r"url\(\s*['\"]?(?:https?:|file:|//)",
                            f"{name} has external URL in {value!r}",
                        )


    def test_manifest_file_exists(self):
        self.assertTrue(MANIFEST_PATH.exists(), "branding-manifest.json must exist in root")

    def test_asset_filenames_end_with_svg(self):
        for name in self.manifest["assets"]:
            with self.subTest(asset=name):
                self.assertTrue(name.endswith(".svg"), f"Asset {name} does not have .svg extension")
    
    def test_digest_format_validity(self):
        """Verify digest format: sha256:HEX."""
        for name, entry in self.manifest["assets"].items():
            with self.subTest(asset=name, digest_type="canonical_sha256"):
                digest = entry["canonical_sha256"]
                self.assertTrue(digest.startswith("sha256:"), f"canonical_sha256 should start with 'sha256:'")
                hex_part = digest[7:]
                self.assertEqual(len(hex_part), 64, "SHA-256 hex should be 64 characters")
                self.assertTrue(all(c in "0123456789abcdef" for c in hex_part), "digest should be valid hex")
            with self.subTest(asset=name, digest_type="bytes_sha256"):
                digest = entry["bytes_sha256"]
                self.assertTrue(digest.startswith("sha256:"), f"bytes_sha256 should start with 'sha256:'")
                hex_part = digest[7:]
                self.assertEqual(len(hex_part), 64, "SHA-256 hex should be 64 characters")
                self.assertTrue(all(c in "0123456789abcdef" for c in hex_part), "digest should be valid hex")

    def test_assets_have_no_scripts_or_event_handlers(self):
        for name in self.manifest["assets"]:
            with self.subTest(asset=name):
                root = ElementTree.parse(ROOT / name).getroot()
                for element in root.iter():
                    tag = element.tag.split("}")[-1]
                    self.assertNotEqual(
                        tag, "script", f"{name} embeds a <script> element"
                    )
                    self.assertNotIn(
                        "{http://www.w3.org/1999/xhtml}",
                        element.tag,
                        f"{name} embeds a foreign xhtml element",
                    )
                    for attribute, value in element.attrib.items():
                        local_attribute = attribute.split("}")[-1]
                        self.assertFalse(
                            local_attribute.lower().startswith("on"),
                            f"{name} has event handler attribute {attribute!r}",
                        )
                        self.assertNotIn(
                            "javascript:",
                            value.lower(),
                            f"{name} has a javascript: URI in {attribute!r}",
                        )


if __name__ == "__main__":
    unittest.main()

