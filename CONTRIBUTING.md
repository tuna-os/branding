# Contributing to branding

`branding` holds the canonical marks (SVGs) for the TunaOS variants. It also
holds the machine-readable asset manifest (`branding-manifest.json`) that
downstream consumers — installers, docs, ISO welcome screens — pin against
and verify.
There is no application to build here; contributions are mostly new or
updated SVG marks, manifest updates, doc changes, and the Python test suite
in `tests/`.

## Proposing or updating a brand asset

1. For anything beyond a small fix, open an issue first that describes the
   change (new variant, palette tweak, etc.).
2. Follow the existing visual system that `README.md` describes.
   `tests/test_branding.py` enforces these properties:
   - A 128x128 viewBox.
   - One accent color per variant, and `#0B1B2B` (abyss) for detail color.
   - The real field mark of the species.
   - No external references (fonts, images, `url()`).
3. After you change an SVG, update its digest in `branding-manifest.json` from
   the repository root:

   ```bash
   asset=<name>.svg
   digest=$(sha256sum "$asset" | cut -d ' ' -f 1)
   jq --arg asset "$asset" --arg digest "sha256:$digest" \
     '.assets[$asset] = $digest' branding-manifest.json > branding-manifest.json.new
   mv branding-manifest.json.new branding-manifest.json
   ```

   Keep the manifest update in the same commit as the SVG change. Make sure
   that each root SVG has an entry in the manifest, and that the manifest has
   no other entries (see the `diff` check in `README.md`).

## Running the test suite

```bash
python3 -m unittest discover -s tests
```

The suite validates the manifest schema and makes sure that the manifest
matches the set of root SVGs. It also checks the SHA-256 digests, the 128x128
viewBox, and that no file has external references. Run the suite (and the
manual `jq`/`sha256sum` checks in `README.md`) before you open a pull request.

## Code style

[Ruff](https://docs.astral.sh/ruff/) lints the Python test suite
(the configuration is in `ruff.toml`):

```bash
ruff check tests/
```

## Branch and PR convention

Use a short, prefixed branch name that describes the change (e.g. `fix/`,
`docs/`, `feat/`, `chore/`), matching the convention used across `tuna-os`
repositories, and reference any issue the PR addresses.

## Reporting issues

Open an issue in this repository. For anything security-related, use the
private channel described in `tuna-os/.github`'s `SECURITY.md`, not a
public issue.
