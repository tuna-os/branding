# AGENTS.md — agent guide for tuna-os/branding

The TunaOS identity: lettermark wordmarks (`wordmarks/`) and Noto emoji marks
(`marks/`). This repo is **source assets plus a contract**, not an
application: the SVGs are the product, and `branding-manifest.json` is what
lets consumers trust a copy.

The files are copies. `scripts/branding/make-lettermarks.py` in tuna-os/tunaOS
generates them and is the source of truth. Change the generator there, then
copy the output here. Sources and licenses are in [`NOTICE`](NOTICE).

Human-facing docs: [`README.md`](README.md) (the two kinds of mark, usage
rules and manifest checks), [`CONTRIBUTING.md`](CONTRIBUTING.md).

## The one rule that will bite you

**Editing an SVG without regenerating its digests breaks the build.**
`branding-manifest.json` keeps two digest maps for every `.svg` in `marks/` and
`wordmarks/`: `assets` (exact bytes) and `canonical_assets` (canonical XML).
`tests/test_branding.py` compares each file against `assets`. Any byte-level
change — including an editor adding a trailing newline — invalidates the entry.
`tests/test_branding_manifest_tool.py` requires the committed manifest to equal
what the tool below writes, so a hand edit of `assets` alone fails the suite.

```bash
python3 scripts/branding_manifest.py update
```

Adding or deleting a mark means updating the manifest too: the test asserts the
manifest names **every** SVG in `marks/` and `wordmarks/` and nothing else.
The same command adds and removes entries. No SVG may sit at the repository root.

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
- Allowlist: SVG namespace only, and only the elements in `ALLOWED_ELEMENTS`
  (so no `<style>`, `<script>`, `<text>`, `<image>`, `<a>`, `<set>`,
  `<foreignObject>`). No `<!DOCTYPE>`, no processing instruction. Every `url(`
  points at `#id`; no attribute value has a backslash or a quote. Namespaced
  attributes: `xlink:href`, `xml:space`, `xml:lang` only.
- No attribute is an `on*` event handler, and no attribute contains a
  `javascript:` URI.
- The manifest and the `marks/` + `wordmarks/` SVG set match exactly.

> **CI runs the suite on every push and pull request** (`.github/workflows/ci.yml`).
> The `required-checks` job is the terminal required check: it fails if the
> contract suite or lint job did not succeed. Still run the suite locally
> before opening a PR — CI catching a broken digest costs you a round trip.

Two other workflows also gate pull requests, see
[`CONTRIBUTING.md`](CONTRIBUTING.md#other-checks-on-a-pull-request):
`actions-security.yml` (`actions.lock` verify + zizmor, every PR) and
`ste.yml` (Prose: STE lint of `README.md` and `CONTRIBUTING.md` on Markdown
changes, `.ste-budget` is `0`, so a docs-only PR can go red).

## Upstream check

`python3 scripts/check_upstream.py <tunaOS checkout>` compares each copy with
its tunaOS source as `NOTICE` maps it. It reports missing, extra and differing
copies, and exits 1 if any. It needs a local checkout, so it is not part of the
contract suite or `required-checks`. `.github/workflows/upstream-sync.yml` runs
it daily and on pull requests that change `marks/`, `wordmarks/` or the script;
that job is advisory. `tests/test_check_upstream.py` covers it on fixture trees.

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
