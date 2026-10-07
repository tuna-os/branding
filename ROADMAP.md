# TunaOS Branding — Roadmap

**Last updated**: 2026-10-07 | **Maintainer**: tuna-os (hanthor)

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
- **Distribution**: **unversioned** — no tags, no releases. Consumers
  (tunaos `build_scripts/checks/verify-branding*.sh`) assert built images
  carry correct branding, but the source itself has no release contract.
- **Validation**: `tests/test_branding.py` validates the manifest and SVG asset
  contract locally. Automated CI execution is still outstanding (#9).
- **Health**: 2 open issues — versioned consumer sync contract (#7),
  validation-suite CI integration (#9).

### Priorities

| Priority | Item | Tracking | Status |
|----------|------|----------|--------|
| P0 | Versioned release contract — scope + versioning strategy decision | #66 | 🔴 **Blocked (needs-direction)** |
| P0.1 | Cross-repo asset sync: fisherman, bootc-installer — depends on #66 | #70 | 🔴 **Blocked (P0 dependency)** |
| P1 | Run the existing manifest + SVG validation suite in CI | #9 | 🟡 In progress |
| P2 | Scope clarification: README source-of-truth claim vs. reality (#63 audit) | #63 | 🔴 **Blocked (maintainer decision)** |

---

## Quarterly Goals

### Current Quarter (2026 Q3) — **RETROSPECTIVE**

**Theme**: make identity versioned

| Goal | Owner | Tracking | Status |
|------|-------|----------|--------|
| First tagged release + consumer contract doc | hanthor | #7 / #66 | 🔴 **Not started** — blocked on #66 strategy decision |
| Manifest validation enforced in CI | hanthor | #9 | 🟡 **In progress** — PR ready, awaiting merge |

### Next Quarter (2026 Q4) — **PROVISIONAL** (waiting on #66 decision)

**Theme**: versioned distribution + scale foundation

| Gate | Owner | Tracking | Dependencies | Est. Status |
|------|-------|----------|--------------|--------|
| **#66 decision lands** (A/B/C) — defines scope and versioning model | hanthor | #66 | None — **critical path start** | 🔴 Unstarted |
| CI validation merged + running (#9) | hanthor | #9 | None — parallel | 🟡 Ready for merge |
| Consumer sync PRs for fisherman + bootc-installer | TBD | #70 | **Depends on #66** (versioning strategy) | ⬜ Blocked |
| README scope clarification | hanthor | #63 | **Depends on #66** (brand-role decision) | ⬜ Blocked |
| New-variant SOP documented (hummingbird/gurnard) | tuna-os | org tracking | **Depends on #66** + #70 merged | ⬜ Blocked |

**Q4 Critical Path**: #66 decision → #9 merge → #70 implementation → #63 closure → scale

---

*ROADMAP added by strategist agent (ACMM L6 — full mode). Signed-off-by: hanthor-hive-agent[bot] <290068839+hanthor-hive-agent[bot]@users.noreply.github.com>*
