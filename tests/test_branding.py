import hashlib
import json
import unittest
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "branding-manifest.json"
SVG_NAMESPACE = "http://www.w3.org/2000/svg"
XLINK_HREF = "{http://www.w3.org/1999/xlink}href"


class BrandingContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    def test_manifest_schema(self):
        self.assertEqual(self.manifest["schema_version"], 1)
        self.assertEqual(self.manifest["source"], "https://github.com/tuna-os/branding")
        self.assertIsInstance(self.manifest["assets"], dict)
        self.assertTrue(self.manifest["assets"])

    def test_manifest_contains_every_and_only_root_svg(self):
        files = {path.name for path in ROOT.glob("*.svg")}
        self.assertEqual(set(self.manifest["assets"]), files)

    def test_asset_digests_match_manifest(self):
        for name, expected in self.manifest["assets"].items():
            with self.subTest(asset=name):
                digest = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                self.assertEqual(expected, f"sha256:{digest}")

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


if __name__ == "__main__":
    unittest.main()

