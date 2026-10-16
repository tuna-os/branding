# TunaOS variant branding

Flat vector marks for every TunaOS variant, drawn as one system. All marks
use the same geometry language and one accent color per variant. The real
field mark of each species identifies it, not a palette swap.

| Mark | Accent | Field mark |
|---|---|---|
| `tunaos.svg` | `#2EC4B6` sonar | Master mark — roundel + fish |
| `albacore.svg` | `#7FB7D9` ice | Very long pectoral fin |
| `yellowfin.svg` | `#F4C542` yellow | Sickle dorsal/anal fins + finlets |
| `skipjack.svg` | `#6C8EF5` periwinkle | Horizontal belly stripes |
| `bonito.svg` | `#F4A259` coral | Oblique back stripes |
| `marlin.svg` | `#3D7BF4` cobalt | Spear bill + sail dorsal |
| `flounder.svg` | `#C4915C` sand | Flat oval, both eyes on one side, speckles |
| `grouper.svg` | `#C75146` red | Deep body, downturned mouth, spiny dorsal, spots |
| `guppy.svg` | `#E05299` magenta | Tiny body, huge two-tone fan tail |

Detail color everywhere: `#0B1B2B` (abyss) — mid-tone accents keep the marks
legible on both light and dark backgrounds. All files are 128×128 viewBox,
self-contained (no external refs), safe for Flatpak/live-ISO offline use.

## Usage

- Installer Source-step cards: render at 96 px.
- Welcome pages / ISO boot menus: 128–512 px, scale freely.
- These are the source of truth. Consumers should pin a commit or release from
  this repository and verify copied files against `branding-manifest.json`.
- The installer consumer is
  [`tuna-os/fisherman:data/images/`](https://github.com/tuna-os/fisherman/tree/main/data/images/).
  Update its pin and vendored assets together; do not copy an unversioned branch
  tip.

`branding-manifest.json` is the machine-readable asset contract. Its
`schema_version` covers the manifest format. Each asset entry binds a name to:
- `canonical_sha256`: SHA-256 digest of the normalized SVG form (attribute-sorted,
  whitespace-normalized, comments removed) — invariant across build pipelines
- `bytes_sha256`: SHA-256 of the raw file — for exact-copy verification

The `revision` field records the commit this manifest describes, so consumers can
pin a specific version and verify they have the right assets.

## Maintaining the manifest

When you change an SVG on purpose, update both digests and the revision in
`branding-manifest.json` from the repository root:

```bash
asset=albacore.svg
bytes_digest=$(sha256sum "$asset" | cut -d ' ' -f 1)
canonical_digest=$(python3 normalize_svg.py --digest "$asset" | cut -d ':' -f 2)
revision=$(git rev-parse HEAD)
jq --arg asset "$asset" --arg bytes "sha256:$bytes_digest" --arg canonical "sha256:$canonical_digest" --arg rev "$revision" \
  '.assets[$asset].bytes_sha256 = $bytes | .assets[$asset].canonical_sha256 = $canonical | .revision = $rev' \
  branding-manifest.json > branding-manifest.json.new
mv branding-manifest.json.new branding-manifest.json
```

Keep the manifest update in the same commit as the SVG change. Before you commit,
verify every declared asset and that all assets have both digest types:

```bash
jq -r '.assets | to_entries[] | "\(.value.bytes_sha256 | sub("sha256:"; ""))  \(.key)"' \
  branding-manifest.json | sha256sum --check --strict

diff -u \
  <(find . -maxdepth 1 -type f -name '*.svg' -printf '%f\n' | sort) \
  <(jq -r '.assets | keys[]' branding-manifest.json | sort)

jq '.assets | to_entries[] | select(.value.canonical_sha256 == null or .value.bytes_sha256 == null) | .key' \
  branding-manifest.json | wc -l | grep '^0$'
```

## Running Tests

The Python tests in `tests/test_branding.py` validate the manifest schema,
the SVG dimensions (128x128) and the SHA-256 digests (both canonical and raw-byte).
They also make sure that the asset set is complete and that no file has external
references.

Run the test suite using Python's standard `unittest` module:

```bash
python3 -m unittest discover -s tests
```

## Canonical Form Verification

The `normalize_svg.py` utility normalizes SVGs to canonical form for verification.
This ensures that an SVG that has been through a build pipeline (whitespace
removed, comments stripped, attributes reordered) is still verifiable against the
manifest's canonical digest.

Usage:

```bash
# Compute canonical digest of an asset
python3 normalize_svg.py --digest albacore.svg

# Normalize an SVG file to canonical form (for inspection)
python3 normalize_svg.py albacore.svg -o normalized-albacore.svg
```

Consumers can use this utility to verify that an SVG they have (possibly
modified by build tools) still represents the canonical asset from this
repository.

## License

CC-BY-4.0 — see [LICENSE](LICENSE). You can use these marks with attribution
to refer to the TunaOS project, for example in installers, docs, and community
content. Such use does not imply endorsement by the TunaOS project.
