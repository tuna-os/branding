# TunaOS Branding — Roadmap

**Last updated**: 2026-09-08 | **Maintainer**: tuna-os (hanthor)

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
- **Validation**: `.github/workflows/ci.yml` runs the manifest and SVG contract
  suite plus Ruff on every push and pull request. Its `required-checks` job is
  the stable branch-protection boundary (#9, #37).
- **Health**: The versioned consumer sync contract remains open (#7). Automated
  validation is complete (#9, #37).

### Priorities

| Priority | Item | Tracking | Status |
|----------|------|----------|--------|
| P0 | Versioned release contract — tags + documented consumer pin | #7 | 🟡 Open |
| P1 | Run the existing manifest + SVG validation suite in CI | #9, #37 | ✅ Complete |
| P2 | ROADMAP-coverage entry in org ROADMAP tally | #1295 | ⬜ Not started |

---

## Quarterly Goals

### Current Quarter (2026 Q3)

**Theme**: make identity versioned

| Goal | Owner | Tracking | Status |
|------|-------|----------|--------|
| First tagged release + consumer contract doc | hanthor | #7 | ⬜ Not started |
| Manifest validation enforced in CI | hanthor | #9, #37 | ✅ Complete |

### Next Quarter (2026 Q4)

**Theme**: scale to new variants

| Goal | Owner | Tracking | Status |
|------|-------|----------|--------|
| New-variant mark process (hummingbird/gurnard et al.) documented | tuna-os | (org variant tracking) | ⬜ Not started |

---

*ROADMAP added by strategist agent (ACMM L6 — full mode). Signed-off-by: hanthor-hive-agent[bot] <290068839+hanthor-hive-agent[bot]@users.noreply.github.com>*
