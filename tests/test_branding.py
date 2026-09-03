import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "branding-manifest.json"
SVG_NAMESPACE = "http://www.w3.org/2000/svg"
XLINK_HREF = "{http://www.w3.org/1999/xlink}href"

sys.path.insert(0, str(ROOT / "tools"))

import verify_assets  # noqa: E402  (path set above so the checker is importable)


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
                self.assertEqual(expected, verify_assets.file_digest(ROOT / name))

    def test_repository_root_satisfies_the_checker(self):
        # Same contract as the two tests above, exercised through the entry
        # point consumers run, so the two cannot drift apart.
        manifest = verify_assets.load_manifest(MANIFEST_PATH)
        self.assertEqual([], verify_assets.verify_directory(manifest, ROOT))

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


class AssetCheckerTests(unittest.TestCase):
    """The checker must fail on the cases the manifest exists to catch."""

    def setUp(self):
        self.manifest = verify_assets.load_manifest(MANIFEST_PATH)
        self.directory = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.directory)
        for name in self.manifest["assets"]:
            shutil.copy2(ROOT / name, self.directory / name)

    def test_clean_copy_verifies(self):
        self.assertEqual([], verify_assets.verify_directory(self.manifest, self.directory))

    def test_modified_asset_is_reported(self):
        target = self.directory / "tunaos.svg"
        target.write_bytes(target.read_bytes() + b"<!-- tampered -->")
        problems = verify_assets.verify_directory(self.manifest, self.directory)
        self.assertEqual(1, len(problems))
        self.assertIn("does not match manifest", problems[0])

    def test_missing_asset_is_reported_unless_allowed(self):
        (self.directory / "guppy.svg").unlink()
        self.assertEqual(1, len(verify_assets.verify_directory(self.manifest, self.directory)))
        self.assertEqual(
            [],
            verify_assets.verify_directory(self.manifest, self.directory, allow_missing=True),
        )

    def test_undeclared_asset_is_reported_even_when_missing_allowed(self):
        (self.directory / "extra.svg").write_text("<svg/>", encoding="utf-8")
        problems = verify_assets.verify_directory(
            self.manifest, self.directory, allow_missing=True
        )
        self.assertEqual(1, len(problems))
        self.assertIn("not declared in manifest", problems[0])

    def test_unsupported_schema_version_is_rejected(self):
        manifest_path = self.directory / "branding-manifest.json"
        manifest_path.write_text(json.dumps({"schema_version": 99}), encoding="utf-8")
        with self.assertRaises(ValueError):
            verify_assets.load_manifest(manifest_path)


if __name__ == "__main__":
    unittest.main()

