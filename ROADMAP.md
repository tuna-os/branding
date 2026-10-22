# TunaOS Branding — Roadmap

**Last updated**: 2026-10-22 | **Maintainer**: tuna-os (hanthor)

---

## Mission

Own the TunaOS visual identity as one system: every variant mark drawn in the
same geometry language, one accent color per variant, each species identified
by its real field mark — and delivered to every consumer (variant images,
installers, docs, press kit) as a **versioned contract**, not a file drop.

---

## Current Status

- **Assets**: `tunaos.svg` master mark + per-variant marks (albacore,
  yellowfin, skipjack, bonito, marlin, flounder, grouper, guppy), plus
  `branding-manifest.json`.
- **Distribution**: **unversioned** — this repository has no tags or GitHub
  releases. Issue #7 remains open. `tuna-os/fisherman` currently vendors five
  canonical marks (`albacore`, `bonito`, `skipjack`, `tunaos`, `yellowfin`),
  but has no `branding-manifest.json`, source revision pin, or automated
  digest/freshness check; canonical `marlin`, `flounder`, `grouper`, and
  `guppy` have no consumer path there.
- **Validation**: `tests/test_branding.py` validates the manifest and SVG asset
  contract, enforced in CI (`ci.yml`) on every push and pull request via the
  terminal `required-checks` gate (#9, closed).
- **Health**: 1 open issue — the versioned release and consumer sync contract
  (#7).

### Priorities

| Priority | Item | Tracking | Status |
|----------|------|----------|--------|
| P0 | Versioned release contract — tags + documented consumer pin | #7 | 🟡 Open — zero tags/releases |
| P1 | ROADMAP-coverage entry in org ROADMAP tally | #1295 | ✅ Indexed in `.github/ROADMAP-INDEX.md` |

---

## Quarterly Goals

### Previous Quarter (2026 Q3)

**Theme**: make identity versioned

| Goal | Owner | Tracking | Status |
|------|-------|----------|--------|
| First tagged release + consumer contract doc | hanthor | #7 | ⏸ Carried forward — no tag, release, or consumer pin |
| Manifest validation enforced in CI | hanthor | #9 | ✅ Done |

### Current Quarter (2026 Q4)

**Theme**: version the identity and close the consumer delivery chain

| Goal | Owner | Tracking | Status |
|------|-------|----------|--------|
| Publish first tagged release + document consumer pin | hanthor | #7 | ⬜ Open |
| Deliver all nine canonical marks with manifest/pin/freshness checks in `fisherman` | tuna-os | #7 | ⬜ Open |
| Keep the org ROADMAP index entry current | tuna-os | #1295 | ✅ Done |

### Next Quarter (2027 Q1)

**Theme**: scale to new variants

| Goal | Owner | Tracking | Status |
|------|-------|----------|--------|
| New-variant mark process (hummingbird/gurnard et al.) documented | tuna-os | (org variant tracking) | ⬜ Not started |
