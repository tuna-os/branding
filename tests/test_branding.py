import hashlib
import json
import re
import unittest
from pathlib import Path
from xml.etree import ElementTree
from xml.parsers import expat

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "branding-manifest.json"
SVG_NAMESPACE = "http://www.w3.org/2000/svg"
XLINK_HREF = "{http://www.w3.org/1999/xlink}href"
ASSET_DIRS = ("marks", "wordmarks")
XML_NAMESPACE = "{http://www.w3.org/XML/1998/namespace}"

# Static drawing elements only. None of them loads a resource or runs code, so
# an asset built from them is self-contained whatever renders it. Elements that
# are not listed (style, script, image, text, a, set, animate, foreignObject,
# filter) fail the suite.
ALLOWED_ELEMENTS = frozenset(
    {
        "circle",
        "clipPath",
        "defs",
        "desc",
        "ellipse",
        "g",
        "line",
        "linearGradient",
        "mask",
        "path",
        "polygon",
        "polyline",
        "radialGradient",
        "rect",
        "stop",
        "svg",
        "title",
        "use",
    }
)
# xml:base is not listed: it changes the document that "#id" refers to.
ALLOWED_NAMESPACED_ATTRIBUTES = frozenset(
    {XLINK_HREF, f"{XML_NAMESPACE}space", f"{XML_NAMESPACE}lang"}
)


class _DeclarationRecorder(ElementTree.TreeBuilder):
    """Record the processing instructions that ElementTree parses and then drops."""

    def __init__(self):
        super().__init__()
        self.declarations = []

    def pi(self, target, data=None):
        self.declarations.append(f"<?{target}?> processing instruction")
        return super().pi(target, data)


def _has_doctype(data):
    """Return whether the XML has a DOCTYPE.

    This asks expat. Without its C accelerator, ElementTree does not pass a
    DOCTYPE that has only an internal subset to the tree builder.
    """
    found = []
    parser = expat.ParserCreate()
    parser.StartDoctypeDeclHandler = lambda *declaration: found.append(declaration)
    parser.Parse(data, True)
    return bool(found)


def svg_allowlist_problems(data):
    """Return each reason an SVG is outside the allowlist. Empty means inside."""
    builder = _DeclarationRecorder()
    parser = ElementTree.XMLParser(target=builder)
    parser.feed(data)
    root = parser.close()
    problems = ["<!DOCTYPE> declaration"] if _has_doctype(data) else []
    problems += builder.declarations
    for element in root.iter():
        namespace, _, local_name = element.tag.rpartition("}")
        if namespace != f"{{{SVG_NAMESPACE}" or local_name not in ALLOWED_ELEMENTS:
            problems.append(f"element {element.tag!r} is not in the allowlist")
        for attribute, value in element.attrib.items():
            if attribute.startswith("{") and attribute not in ALLOWED_NAMESPACED_ATTRIBUTES:
                problems.append(f"attribute {attribute!r} is not in the allowlist")
            # A CSS escape or a quoted string can spell a URL without "url(".
            if any(character in value for character in "\\'\""):
                problems.append(f"attribute {attribute!r} has a backslash or a quote")
            # CSS function names are case-insensitive.
            for match in re.finditer(r"url\(", value, re.IGNORECASE):
                if not value.startswith("#", match.end()):
                    problems.append(f"attribute {attribute!r} has a url() that is not #id")
    return problems


def _svg(body, prolog=""):
    return f'{prolog}<svg xmlns="{SVG_NAMESPACE}" viewBox="0 0 128 128">{body}</svg>'.encode()


# Each sample passed the suite before the allowlist. The second item is the
# problem that the allowlist must report for it.
UNSAFE_SVG_SAMPLES = {
    "style element": (
        _svg("<style>@import url(https://example.invalid/a.css);</style>"),
        "style' is not in the allowlist",
    ),
    "xml-stylesheet": (
        _svg("", '<?xml-stylesheet href="https://example.invalid/a.css"?>'),
        "<?xml-stylesheet?> processing instruction",
    ),
    "doctype": (
        _svg("", '<!DOCTYPE svg SYSTEM "https://example.invalid/a.dtd">'),
        "<!DOCTYPE> declaration",
    ),
    "doctype with only an internal subset": (
        _svg("", '<!DOCTYPE svg [<!ENTITY x "y">]>'),
        "<!DOCTYPE> declaration",
    ),
    "uppercase URL function": (
        _svg('<path style="fill:URL(https://example.invalid/a.svg#x)"/>'),
        "url() that is not #id",
    ),
    "uppercase scheme": (
        _svg('<path style="fill:url(HTTPS://example.invalid/a.svg#x)"/>'),
        "url() that is not #id",
    ),
    "relative file": (
        _svg('<path style="fill:url(../other.svg#x)"/>'),
        "url() that is not #id",
    ),
    "data URI": (
        _svg('<rect style="fill:url(data:image/png;base64,iVBORw0KGgo=)"/>'),
        "url() that is not #id",
    ),
    "CSS escape": (
        _svg('<path style="fill:\\75rl(https://example.invalid/a.svg#x)"/>'),
        "has a backslash or a quote",
    ),
    "quoted image-set": (
        _svg("<rect style='mask-image:image-set(\"https://example.invalid/a.png\" 1x)'/>"),
        "has a backslash or a quote",
    ),
    "set on a link": (
        _svg('<a href="#"><set attributeName="href" to="java&#9;script:alert(1)"/></a>'),
        "set' is not in the allowlist",
    ),
    "foreignObject": (
        _svg('<foreignObject><math xmlns="http://www.w3.org/1998/Math/MathML"/></foreignObject>'),
        "foreignObject' is not in the allowlist",
    ),
    "live text": (
        _svg('<text font-family="Baloo 2">Tuna</text>'),
        "text' is not in the allowlist",
    ),
    "embedded image": (
        _svg('<image href="#x"/>'),
        "image' is not in the allowlist",
    ),
    "xml:base": (
        _svg('<use xml:base="https://example.invalid/a.svg" href="#x"/>'),
        "base' is not in the allowlist",
    ),
}


class BrandingContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    def test_manifest_schema(self):
        self.assertEqual(self.manifest["schema_version"], 1)
        self.assertEqual(self.manifest["source"], "https://github.com/tuna-os/branding")
        self.assertIsInstance(self.manifest["assets"], dict)
        self.assertTrue(self.manifest["assets"])

    def test_manifest_contains_every_and_only_asset_svg(self):
        files = {
            path.relative_to(ROOT).as_posix()
            for directory in ASSET_DIRS
            for path in (ROOT / directory).glob("*.svg")
        }
        self.assertEqual(set(self.manifest["assets"]), files)
        self.assertEqual(list(ROOT.glob("*.svg")), [], "SVGs belong in marks/ or wordmarks/")

    def test_every_mark_has_light_and_dark_wordmark(self):
        marks = {path.stem for path in (ROOT / "marks").glob("*.svg")} - {"tunaos"}
        wordmarks = {path.stem for path in (ROOT / "wordmarks").glob("*.svg")}
        for variant in marks:
            with self.subTest(variant=variant):
                self.assertIn(variant, wordmarks)
                self.assertIn(f"{variant}-dark", wordmarks)

    def test_asset_digests_match_manifest(self):
        for name, expected in self.manifest["assets"].items():
            with self.subTest(asset=name):
                digest = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                self.assertEqual(expected, f"sha256:{digest}")

    def test_assets_are_parseable_svgs(self):
        for name in self.manifest["assets"]:
            with self.subTest(asset=name):
                root = ElementTree.parse(ROOT / name).getroot()
                self.assertEqual(root.tag, f"{{{SVG_NAMESPACE}}}svg")
                self.assertTrue(root.attrib.get("viewBox"), f"{name} has no viewBox")

    def test_emoji_marks_are_128_square(self):
        for name in self.manifest["assets"]:
            if not name.startswith("marks/"):
                continue
            with self.subTest(asset=name):
                root = ElementTree.parse(ROOT / name).getroot()
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
        self.assertTrue(MANIFEST_PATH.exists(), "branding-manifest.json must exist")

    def test_asset_filenames_end_with_svg(self):
        for name in self.manifest["assets"]:
            with self.subTest(asset=name):
                self.assertTrue(name.endswith(".svg"), f"Asset {name} does not have .svg extension")

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

    def test_assets_use_only_allowlisted_svg(self):
        for name in self.manifest["assets"]:
            with self.subTest(asset=name):
                self.assertEqual(svg_allowlist_problems((ROOT / name).read_bytes()), [])

    def test_allowlist_accepts_static_svg(self):
        sample = _svg(
            '<defs><linearGradient id="a"><stop offset="0" style="stop-color:#FFF"/>'
            '</linearGradient></defs><title>Tuna</title>'
            '<path style="fill:url(#a);" d="M0 0h1v1z"/><rect fill="url(#a)"/>'
        )
        self.assertEqual(svg_allowlist_problems(sample), [])

    def test_allowlist_rejects_unsafe_svg(self):
        for label, (sample, expected) in UNSAFE_SVG_SAMPLES.items():
            with self.subTest(sample=label):
                problems = svg_allowlist_problems(sample)
                self.assertTrue(
                    any(expected in problem for problem in problems),
                    f"expected {expected!r} in {problems!r}",
                )


if __name__ == "__main__":
    unittest.main()

