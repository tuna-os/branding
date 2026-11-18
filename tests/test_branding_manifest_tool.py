import contextlib
import importlib.util
import io
import json
import re
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "branding-manifest.json"

_spec = importlib.util.spec_from_file_location(
    "branding_manifest", ROOT / "scripts" / "branding_manifest.py"
)
tool = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tool)


class CanonicalDigestTests(unittest.TestCase):
    """The canonical digest ignores packaging noise and nothing else."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)

    def write(self, name, text):
        path = self.dir / name
        path.write_text(text, encoding="utf-8")
        return path

    def body(self, asset):
        """Return the asset with its XML declaration and comments removed."""
        text = (ROOT / asset).read_text(encoding="utf-8")
        text = re.sub(r"^<\?xml[^>]*\?>\s*", "", text)
        return re.sub(r"<!--.*?-->\s*", "", text, flags=re.S)

    def test_attribution_header_and_declaration_do_not_change_digest(self):
        # The shape fisherman vendors: the raw Noto file, a different XML
        # declaration and no attribution comment.
        asset = "marks/tunaos.svg"
        copy = self.write(
            "copy.svg",
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            "<!-- Used unmodified as this application's icon. -->\n" + self.body(asset),
        )
        self.assertNotEqual(tool.file_digest(copy), tool.file_digest(ROOT / asset))
        self.assertEqual(tool.canonical_digest(copy), tool.canonical_digest(ROOT / asset))

    def test_whitespace_stripping_does_not_change_digest(self):
        # GResource preprocess="xml-stripblanks" drops whitespace-only text.
        asset = "wordmarks/tunaos.svg"
        copy = self.write("copy.svg", re.sub(r">\s+<", "><", self.body(asset)))
        self.assertEqual(tool.canonical_digest(copy), tool.canonical_digest(ROOT / asset))

    def test_changed_artwork_changes_digest(self):
        asset = "marks/tunaos.svg"
        body = self.body(asset)
        changes = (
            ("#1483BC", "#1483BD"),
            ('viewBox="0 0 128 128"', 'viewBox="0 0 128 127"'),
        )
        for old, new in changes:
            with self.subTest(change=new):
                self.assertIn(old, body)
                copy = self.write("copy.svg", body.replace(old, new, 1))
                self.assertNotEqual(
                    tool.canonical_digest(copy), tool.canonical_digest(ROOT / asset)
                )


class VerifyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)

    def test_exact_copy_verifies_as_exact(self):
        self.assertEqual(
            tool.verify_copy(self.manifest, "marks/bonito.svg", ROOT / "marks/bonito.svg"),
            (True, "exact"),
        )

    def test_commented_copy_verifies_as_canonical(self):
        copy = self.dir / "tunaos.svg"
        text = (ROOT / "marks/tunaos.svg").read_text(encoding="utf-8")
        copy.write_text(re.sub(r"<!--.*?-->\s*", "", text, flags=re.S), encoding="utf-8")
        self.assertEqual(
            tool.verify_copy(self.manifest, "marks/tunaos.svg", copy), (True, "canonical")
        )

    def test_rejects_copy_with_doctype(self):
        text = (ROOT / "marks/tunaos.svg").read_text(encoding="utf-8")
        doctypes = (
            '<!DOCTYPE svg SYSTEM "https://example.invalid/a.dtd">',
            '<!DOCTYPE svg [<!ENTITY x "y">]>',
            '<!DOCTYPE svg [<!ENTITY % r SYSTEM "https://example.invalid/a.dtd"> %r;'
            ' <!ATTLIST svg onload CDATA "alert(1)">]>',
        )
        for index, doctype in enumerate(doctypes):
            with self.subTest(doctype=doctype):
                copy = self.dir / f"doctype{index}.svg"
                copy.write_text(text.replace("<svg", doctype + "<svg", 1), encoding="utf-8")
                ok, detail = tool.verify_copy(self.manifest, "marks/tunaos.svg", copy)
                self.assertFalse(ok)
                self.assertIn("DOCTYPE", detail)

    def test_rejects_other_asset_unknown_name_missing_and_unparseable_file(self):
        garbage = self.dir / "garbage.svg"
        garbage.write_text("not xml", encoding="utf-8")
        cases = {
            "other asset": ("marks/marlin.svg", ROOT / "marks/tunaos.svg"),
            "unknown asset": ("marks/nope.svg", ROOT / "marks/tunaos.svg"),
            "missing file": ("marks/tunaos.svg", self.dir / "missing.svg"),
            "unparseable": ("marks/tunaos.svg", garbage),
        }
        for case, (asset, copy) in cases.items():
            with self.subTest(case=case):
                ok, _ = tool.verify_copy(self.manifest, asset, copy)
                self.assertFalse(ok)

    def test_cli_exit_status(self):
        good = f"marks/tunaos.svg={ROOT / 'marks/tunaos.svg'}"
        bad = f"marks/marlin.svg={ROOT / 'marks/tunaos.svg'}"
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(tool.main(["verify", "--manifest", str(MANIFEST_PATH), good]), 0)
            self.assertEqual(tool.main(["verify", "--manifest", str(MANIFEST_PATH), good, bad]), 1)


class ManifestIsCurrentTests(unittest.TestCase):
    def test_canonical_assets_name_every_asset(self):
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        self.assertEqual(set(manifest["canonical_assets"]), set(tool.asset_names(ROOT)))
        self.assertEqual(set(manifest["canonical_assets"]), set(manifest["assets"]))

    def test_update_reproduces_committed_manifest(self):
        # The committed manifest is exactly what `branding_manifest.py update`
        # writes, so both digest maps are current and nothing is hand-edited.
        self.assertEqual(
            tool.render_manifest(tool.build_manifest(ROOT)),
            MANIFEST_PATH.read_text(encoding="utf-8"),
            "run: python3 scripts/branding_manifest.py update",
        )


if __name__ == "__main__":
    unittest.main()
