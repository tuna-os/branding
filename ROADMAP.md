# TunaOS Branding — Roadmap

**Last updated**: 2026-09-17 | **Maintainer**: tuna-os (hanthor)

---

## Mission

Own the TunaOS visual identity as one system: every variant mark drawn in the
same geometry language, one accent color per variant, each species identified
by its real field mark — and delivered to every consumer (variant images,
installers, docs, press kit) as a **versioned contract**, not a file drop.

---

## Current Status (September 2026)

- **Assets**: `tunaos.svg` master mark + per-variant marks (albacore,
  yellowfin, skipjack, bonito, marlin, flounder, grouper, guppy), plus
  `branding-manifest.json`.
- **Distribution**: **unversioned** — no tags, no releases. Consumers
  (tunaos `build_scripts/checks/verify-branding*.sh`) assert built images
  carry correct branding, but the source itself has no release contract.
- **Validation**: **CI Enforced** — `tests/test_branding.py` contract suite and
  ruff linting are fully integrated into `.github/workflows/ci.yml` (#9, #37).
- **Health**: Open issues — versioned consumer sync contract (#7), codecov integration (#44).

### Priorities

| Priority | Item | Tracking | Status |
|----------|------|----------|--------|
| P0 | Versioned release contract — `v0.1.0` tag + documented consumer pin contract | #7 | 🟡 Open |
| P1 | Run manifest + SVG validation suite in CI | #9 | 🟢 Completed |
| P2 | Org variant expansion — add marks for hummingbird, gurnard, and bootsahi | #13 | 🟡 Open |
| P3 | ROADMAP-coverage entry in org ROADMAP tally | #1295 | 🟢 Completed |

---

## Quarterly Goals

### Current Quarter (2026 Q3 Exit)

**Theme**: make identity versioned and validated

| Goal | Owner | Tracking | Status |
|------|-------|----------|--------|
| Manifest validation enforced in CI | hanthor | #9 | 🟢 Completed |
| First tagged release (`v0.1.0`) + consumer contract doc | hanthor | #7 | 🟡 Open |

### Next Quarter (2026 Q4)

**Theme**: versioned distribution & multi-desktop expansion

| Goal | Owner | Tracking | Status |
|------|-------|----------|--------|
| Publish `v0.1.0` tagged release with signed release assets | tuna-os | #7 | ⬜ Not started |
| New-variant marks (hummingbird, gurnard, bootsahi) integrated into manifest | tuna-os | #13 | ⬜ Not started |
| Downstream consumer pin verification (tunaos, bootc-installer, docs) | tuna-os | #7 | ⬜ Not started |

---

*ROADMAP updated by strategist agent (ACMM L6 — full mode).*
