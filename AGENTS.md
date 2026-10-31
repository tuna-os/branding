# AGENTS.md — agent guide for tuna-os/branding

The TunaOS identity: lettermark wordmarks (`wordmarks/`) and Noto emoji marks
(`marks/`). This repo is **source assets plus a contract**, not an
application: the SVGs are the product, and `branding-manifest.json` is what
lets consumers trust a copy.

The files are copies. `scripts/branding/make-lettermarks.py` in tuna-os/tunaOS
generates them and is the source of truth. Change the generator there, then
copy the output here. Sources and licenses are in [`NOTICE`](NOTICE).

Human-facing docs: [`README.md`](README.md) (the mark table and usage rules),
[`CONTRIBUTING.md`](CONTRIBUTING.md).

## The one rule that will bite you

**Editing an SVG without regenerating its digest breaks the build.**
`branding-manifest.json` pins a `sha256:` for every `.svg` in `marks/` and `wordmarks/`, and
`tests/test_branding.py` compares each file against it. Any byte-level change —
including an editor adding a trailing newline — invalidates the entry.

```bash
python3 - <<'PY'
import hashlib, json, pathlib
root = pathlib.Path(".")
m = json.loads((root / "branding-manifest.json").read_text())
m["assets"] = {p.as_posix(): "sha256:" + hashlib.sha256(p.read_bytes()).hexdigest()
               for d in ("marks", "wordmarks") for p in sorted(root.glob(f"{d}/*.svg"))}
(root / "branding-manifest.json").write_text(json.dumps(m, indent=2) + "\n")
PY
```

Adding or deleting a mark means updating the manifest too: the test asserts the
manifest names **every** SVG in `marks/` and `wordmarks/` and nothing else.
No SVG may sit at the repository root.

## Checks

```bash
python3 -m unittest discover -s tests -v   # the contract suite
ruff check .                               # py311, line-length 100, E/F/I
```

`tests/test_branding.py` enforces these invariants beyond the digests:

- `schema_version` is `1` and `source` is this repo's URL.
- Every asset parses as SVG with a `viewBox`. Emoji marks use
  `viewBox="0 0 128 128"` exactly.
- Every variant mark has a light and a `-dark` wordmark.
- No external references — `href`/`xlink:href` must start with `#`, and no
  attribute may contain a `url(http…)`, `url(file:…)` or protocol-relative URL.
- Each asset name in the manifest ends in `.svg`.
- No asset contains a `<script>` element or a foreign XHTML element. No
  attribute is an `on*` event handler, and no attribute contains a
  `javascript:` URI.
- The manifest and the `marks/` + `wordmarks/` SVG set match exactly.

> **CI runs the suite on every push and pull request** (`.github/workflows/ci.yml`).
> The `required-checks` job is the terminal required check: it fails if the
> contract suite or lint job did not succeed. Still run the suite locally
> before opening a PR — CI catching a broken digest costs you a round trip.

## Design constraints

These are contract, not taste — the marks are consumed offline:

- **Usage rule.** Wordmark for wide contexts (headers, login, boot splash).
  Emoji mark for small contexts (icons, favicons, terminal).
- **Self-contained.** No external refs, no embedded raster, no web fonts —
  files must work inside a Flatpak sandbox and on a live ISO with no network.
  The wordmark lettering is outlined glyph paths, not text.

## Downstream

These files get **copied** into consumers, not
submoduled. The known consumer is
[`tuna-os/fisherman:data/images/`](https://github.com/tuna-os/fisherman/tree/main/data/images/).
Consumers pin a commit or release and verify their copies against the manifest,
so a digest that disagrees with the file is a supply-chain break for them, not
just a red test here.
