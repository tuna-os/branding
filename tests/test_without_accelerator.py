import subprocess
import sys
import unittest
from pathlib import Path

TESTS = Path(__file__).resolve().parent

# The DOCTYPE tests, in a Python that cannot import the C accelerator. Then
# xml.etree.ElementTree uses its pure-Python parser, as it does on each Python
# that has no _elementtree module.
SCRIPT = """
import sys
sys.modules["_elementtree"] = None
sys.path.insert(0, sys.argv[1])
import unittest
suite = unittest.defaultTestLoader.loadTestsFromNames([
    "test_branding.BrandingContractTests.test_allowlist_rejects_unsafe_svg",
    "test_branding.BrandingContractTests.test_assets_use_only_allowlisted_svg",
    "test_branding_manifest_tool.VerifyTests",
])
result = unittest.TextTestRunner(stream=sys.stderr).run(suite)
sys.exit(0 if result.wasSuccessful() and result.testsRun else 1)
"""


class WithoutAcceleratorTests(unittest.TestCase):
    def test_doctype_checks_do_not_need_the_c_accelerator(self):
        result = subprocess.run(
            [sys.executable, "-c", SCRIPT, str(TESTS)], capture_output=True, text=True
        )
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
