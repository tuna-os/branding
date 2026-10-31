# TunaOS variant branding

The TunaOS identity has two parts. These files are the same marks that ship in
TunaOS images.

- **Wordmark** (`wordmarks/<variant>.svg`, `wordmarks/<variant>-dark.svg`):
  the emoji mark plus the variant name in Baloo 2 lettering. Use the `-dark`
  file on dark backgrounds.
- **Emoji mark** (`marks/<variant>.svg`): one Noto Emoji glyph per variant.
  `marks/tunaos.svg` is the TunaOS master mark (U+1F41F FISH).

The master TunaOS wordmark is `wordmarks/tunaos.svg` and
`wordmarks/tunaos-dark.svg`.

## Usage rule

- Use the **wordmark** in wide contexts: headers, banners, login screens,
  boot splash and installer title areas.
- Use the **emoji mark** in small contexts: app and distro icons, favicons,
  installer cards and terminal output.

## Source of truth

`scripts/branding/make-lettermarks.py` in
[`tuna-os/tunaOS`](https://github.com/tuna-os/tunaOS) generates these files.
This repository holds copies. To change a mark, change the generator in
tunaOS, then copy the output here and update the manifest.

<!-- hive-contribute-plea: donated-compute appeal, keep in sync across repos -->
## Contribute compute — no code needed

**[Donate time with your AI CLI](https://hub.tunaos.org/#contribute).**

Your machine runs one task at a time using your signed-in AI coding CLI.
The relay alternates between eligible **School** (OS) and **Reef** (apps)
hives after each task. If one hive has no work, the other can continue.

The guide covers prerequisites, verified `just` setup, credentials, provider
costs, and how to stop with Ctrl+C. Your subscription quota or API charges apply.
Never post account credentials or API keys in issues or pull requests.

## Usage

- Emoji marks have a 128×128 viewBox. Scale them freely.
- Wordmarks have a wide viewBox. Scale them by height.
- Consumers should pin a commit or release from
  this repository and verify copied files against `branding-manifest.json`.
- The installer consumer is
  [`tuna-os/fisherman:data/images/`](https://github.com/tuna-os/fisherman/tree/main/data/images/).
  Update its pin and vendored assets together; do not copy an unversioned branch
  tip.

`branding-manifest.json` is the machine-readable asset contract. Its
`schema_version` covers the manifest format, while each value binds an asset
name to its SHA-256 digest. Consumers can reject missing, extra, or modified
assets before they package an installer.

## Maintaining the manifest

When you change an SVG on purpose, update its digest in
`branding-manifest.json` from the repository root:

```bash
asset=marks/albacore.svg
digest=$(sha256sum "$asset" | cut -d ' ' -f 1)
jq --arg asset "$asset" --arg digest "sha256:$digest" \
  '.assets[$asset] = $digest' branding-manifest.json > branding-manifest.json.new
mv branding-manifest.json.new branding-manifest.json
```

Replace `marks/albacore.svg` with the asset that changed. Keep the manifest update in
the same commit as the SVG change. Before you commit, verify every declared
asset. Also make sure that each SVG in `marks/` and `wordmarks/` has a manifest entry, and that the
manifest has no entry for a missing file:

```bash
jq -r '.assets | to_entries[] | "\(.value | sub("sha256:"; ""))  \(.key)"' \
  branding-manifest.json | sha256sum --check --strict

diff -u \
  <(find marks wordmarks -maxdepth 1 -type f -name '*.svg' | sort) \
  <(jq -r '.assets | keys[]' branding-manifest.json | sort)
```

Both commands should finish without errors or differences.

## Running Tests

The Python tests in `tests/test_branding.py` validate the manifest schema,
the SVG structure (128x128 for emoji marks) and the SHA-256 digests. They also make sure that
the asset set is complete and that no file has external references.

Run the test suite using Python's standard `unittest` module:

```bash
python3 -m unittest discover -s tests
```

## License

CC-BY-4.0 — see [LICENSE](LICENSE). Third-party parts keep their own
licenses: Noto Emoji is Apache-2.0 and the Baloo 2 glyph outlines are OFL-1.1.
See [NOTICE](NOTICE) for sources and attribution. You can use these marks with attribution
to refer to the TunaOS project, for example in installers, docs, and community
content. Such use does not imply endorsement by the TunaOS project.
