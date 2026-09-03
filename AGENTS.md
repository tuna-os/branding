# AGENTS.md — agent guide for tuna-os/branding

Nine flat vector marks for the TunaOS variants, drawn as one system. This repo
is **source assets plus a contract**, not an application: the SVGs are the
product, and `branding-manifest.json` is what lets consumers trust a copy.

Human-facing docs: [`README.md`](README.md) (the mark table and usage rules),
[`CONTRIBUTING.md`](CONTRIBUTING.md).

## The one rule that will bite you

**Editing an SVG without regenerating its digest breaks the build.**
`branding-manifest.json` pins a `sha256:` for every root-level `.svg`, and
`tests/test_branding.py` compares each file against it. Any byte-level change —
including an editor adding a trailing newline — invalidates the entry.

```bash
python3 - <<'PY'
import hashlib, json, pathlib
root = pathlib.Path(".")
m = json.loads((root / "branding-manifest.json").read_text())
m["assets"] = {p.name: "sha256:" + hashlib.sha256(p.read_bytes()).hexdigest()
               for p in sorted(root.glob("*.svg"))}
(root / "branding-manifest.json").write_text(json.dumps(m, indent=2) + "\n")
PY
```

Adding or deleting a mark means updating the manifest too: the test asserts the
manifest names **every** root SVG and **only** root SVGs.

## Checks

```bash
python3 -m unittest discover -s tests -v   # the contract suite
ruff check .                               # py311, line-length 100, E/F/I
```

`tests/test_branding.py` enforces four invariants beyond the digests:

- `schema_version` is `1` and `source` is this repo's URL.
- Every asset parses as SVG with `viewBox="0 0 128 128"` exactly.
- No external references — `href`/`xlink:href` must start with `#`, and no
  attribute may contain a `url(http…)`, `url(file:…)` or protocol-relative URL.
- The manifest and the root SVG set match exactly.

> **There is no CI in this repository.** No `.github/workflows/` exists, so
> nothing runs the suite on a push or PR. Run it locally before opening a PR —
> a broken digest will otherwise reach consumers silently.

## Design constraints

These are contract, not taste — the marks are consumed offline at small sizes:

- **128×128 viewBox**, always. Consumers render at 96 px (installer cards) and
  128–512 px (welcome pages, ISO boot menus).
- **Self-contained.** No external refs, no embedded raster, no web fonts —
  files must work inside a Flatpak sandbox and on a live ISO with no network.
- **One accent per variant**, with `#0B1B2B` (abyss) for detail. Marks must stay
  legible on both light and dark backgrounds, which is why detail is a mid-tone
  rather than pure black.
- Each species is identified by its **real field mark** (albacore's long
  pectoral fin, guppy's fan tail), not by a palette swap. Keep the geometry
  language consistent across the set when adding one.

## Downstream

These files are the source of truth and get **copied** into consumers, not
submoduled. The known consumer is
[`tuna-os/fisherman:data/images/`](https://github.com/tuna-os/fisherman/tree/main/data/images/).
Consumers pin a commit or release and verify their copies against the manifest,
so a digest that disagrees with the file is a supply-chain break for them, not
just a red test here.
