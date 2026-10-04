# TunaOS Branding — Roadmap

**Last updated**: 2026-10-04 | **Maintainer**: tuna-os (hanthor)

---

## Mission

Own the TunaOS visual identity as one system: every variant mark drawn in the
same geometry language, one accent color per variant, each species identified
by its real field mark — and delivered to every consumer (variant images,
installers, docs, press kit) as a **versioned contract**, not a file drop.

---

## Current Status (Q4 2026 checkpoint)

**Execution stalled**: Both Q3 launch goals (versioned release #7, CI validation #9) remain unstarted 5+ weeks post-planning. The assets and validation suite exist; publication and automation do not.

- **Assets**: `tunaos.svg` master mark + per-variant marks (albacore,
  yellowfin, skipjack, bonito, marlin, flounder, grouper, guppy), plus
  `branding-manifest.json`.
- **Distribution**: **unversioned** — no tags, no releases. Consumers
  (tunaos `build_scripts/checks/verify-branding*.sh`) validate built images,
  but the source has no release contract.
- **Validation**: `tests/test_branding.py` validates the manifest and SVG asset
  contract locally. CI integration (#9) is still blocked.
- **Health**: Same 2 open issues — versioned consumer sync contract (#7),
  validation-suite CI integration (#9). No progress recorded since 08-24.

The repository itself is ACMM L0 compliant and well-structured. The gap is pure
execution: one owner decision (versioning scheme) + one afternoon (tag +
consumer doc) → first release.

### Priorities

| Priority | Item | Tracking | Status | Age |
|----------|------|----------|--------|-----|
| P0 | Versioned release contract — tags + documented consumer pin | #7 | 🔴 Unstarted | 41d |
| P1 | Run the existing manifest + SVG validation suite in CI | #9 | 🔴 Unstarted | 41d |
| P2 | ROADMAP-coverage entry in org ROADMAP tally | #1295 | ⬜ Not started | 41d |

---

## Quarterly Goals

### Current Quarter (2026 Q3)

**Theme**: make identity versioned

| Goal | Owner | Tracking | Status |
|------|-------|----------|--------|
| First tagged release + consumer contract doc | hanthor | #7 | 🔴 Unstarted (41d) |
| Manifest validation enforced in CI | hanthor | #9 | 🔴 Unstarted (41d) |

### Next Quarter (2026 Q4)

**Theme**: scale to new variants

| Goal | Owner | Tracking | Status |
|------|-------|----------|--------|
| New-variant mark process (hummingbird/gurnard et al.) documented | tuna-os | (org variant tracking) | ⬜ Not started |

## Strategic risk

Identity versioning is a prerequisite for multi-variant scaling (#1295) and
consumer trust. The 41-day execution gap suggests either:

- **Staffing**: versioning scheme needs one owner decision; automation (#9) is
  straightforward Python CI addition.
- **Sequencing**: no blocker exists. Both issues are independent and
  implementable in parallel.

No architectural or technical risk; pure execution visibility problem.

---
*Maintained by the strategist agent (ACMM L6 — full mode). Last refresh: 2026-10-04.*
