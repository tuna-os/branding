import contextlib
import importlib.util
import io
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

_spec = importlib.util.spec_from_file_location(
    "check_upstream", ROOT / "scripts" / "check_upstream.py"
)
tool = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tool)

LOGOS = "system_files/usr/share/tunaos/logos"
LETTERMARKS = "system_files/usr/share/tunaos/lettermarks"
PIXMAPS = "system_files/usr/share/pixmaps"


class CheckUpstreamTests(unittest.TestCase):
    """Fixture trees stand in for tunaOS; the suite needs no network."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.upstream = Path(tmp.name) / "tunaOS"
        self.root = Path(tmp.name) / "branding"
        pairs = {
            "marks/tuna.svg": f"{LOGOS}/tuna.svg",
            "marks/tunaos.svg": f"{PIXMAPS}/tunaos.svg",
            "wordmarks/tuna.svg": f"{LETTERMARKS}/tuna.svg",
            "wordmarks/tuna-dark.svg": f"{LETTERMARKS}/tuna-dark.svg",
        }
        for copy, source in pairs.items():
            self.write(self.root / copy, copy)
            self.write(self.upstream / source, copy)

    @staticmethod
    def write(path, text):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def test_in_sync(self):
        self.assertEqual(tool.check(self.upstream, self.root), [])

    def test_missing_copy(self):
        self.write(self.upstream / LOGOS / "stingray.svg", "x")
        self.write(self.upstream / LETTERMARKS / "stingray-dark.svg", "x")
        self.assertEqual(
            [p.split(" (")[0] for p in tool.check(self.upstream, self.root)],
            ["missing: marks/stingray.svg", "missing: wordmarks/stingray-dark.svg"],
        )

    def test_differing_copy(self):
        self.write(self.upstream / PIXMAPS / "tunaos.svg", "changed")
        problems = tool.check(self.upstream, self.root)
        self.assertEqual(len(problems), 1)
        self.assertTrue(problems[0].startswith("differs: marks/tunaos.svg"))

    def test_extra_copy(self):
        self.write(self.root / "wordmarks" / "orphan.svg", "x")
        problems = tool.check(self.upstream, self.root)
        self.assertEqual(len(problems), 1)
        self.assertTrue(problems[0].startswith("extra: wordmarks/orphan.svg"))

    def test_main_exit_codes(self):
        out = contextlib.redirect_stdout(io.StringIO())
        err = contextlib.redirect_stderr(io.StringIO())
        with out, err:
            self.assertEqual(tool.main([str(self.upstream)]), 1)  # real repo lacks fixtures
            self.assertEqual(tool.main([str(self.root)]), 2)  # not a tunaOS tree

    def test_notice_describes_the_mapping(self):
        notice = (ROOT / "NOTICE").read_text(encoding="utf-8")
        for source_dir in [d for _, d in tool.DIRECTORY_MAP] + list(tool.FILE_MAP.values()):
            self.assertIn(source_dir.removeprefix("system_files/"), notice)


if __name__ == "__main__":
    unittest.main()
