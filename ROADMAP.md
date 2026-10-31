# TunaOS Branding — Roadmap

**Last updated**: 2026-08-24 | **Maintainer**: tuna-os (hanthor)

---

## Mission

Own the TunaOS visual identity as one system: a lettermark wordmark and a Noto
emoji mark per variant, generated in tunaOS — and delivered to every consumer (variant images,
installers, docs, press kit) as a **versioned contract**, not a file drop.

---

## Current Status

- **Assets**: `marks/` (Noto emoji marks, `marks/tunaos.svg` master) and
  `wordmarks/` (light and dark lettermarks per variant), copied from tunaOS
  `scripts/branding/make-lettermarks.py` output, plus `branding-manifest.json`.
- **Distribution**: **unversioned** — no tags, no releases. Consumers
  (tunaos `build_scripts/checks/verify-branding*.sh`) assert built images
  carry correct branding, but the source itself has no release contract.
- **Validation**: `tests/test_branding.py` validates the manifest and SVG asset
  contract, enforced in CI (`ci.yml`) on every push and pull request via the
  terminal `required-checks` gate (#9, closed).
- **Health**: 1 open issue — versioned consumer sync contract (#7).

### Priorities

| Priority | Item | Tracking | Status |
|----------|------|----------|--------|
| P0 | Versioned release contract — tags + documented consumer pin | #7 | 🟡 Open |
| P1 | ROADMAP-coverage entry in org ROADMAP tally | #1295 | ⬜ Not started |

---

## Quarterly Goals

### Current Quarter (2026 Q3)

**Theme**: make identity versioned

| Goal | Owner | Tracking | Status |
|------|-------|----------|--------|
| First tagged release + consumer contract doc | hanthor | #7 | ⬜ Not started |
| Manifest validation enforced in CI | hanthor | #9 | ✅ Done |

### Next Quarter (2026 Q4)

**Theme**: scale to new variants

| Goal | Owner | Tracking | Status |
|------|-------|----------|--------|
| New-variant mark process (hummingbird/gurnard et al.) documented | tuna-os | (org variant tracking) | ⬜ Not started |
