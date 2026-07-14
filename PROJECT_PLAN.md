# PROJECT_PLAN.md

> **Provenance note:** the authoritative PROJECT_PLAN.md was referenced by
> HIERARCHICAL_KAPPA_PLAN.md and the 2026-07-14 session instructions but was
> never checked into the repo. This file is a reconstruction of the phases
> those documents rely on, written so cross-references resolve. Replace with
> the authoritative version if one exists; Phase 1 below already reflects the
> two-window decision (REFERENCE.md §4).

## Phase 1 — Data expansion (two-window design)

Supersedes the original "download 20+ seasons" plan.

- **Behavioral analysis window: 2021-22 through 2025-26** (shufinskiy seasons
  2021–2025). All behavioral estimation (κ, λ, hazard, DP, decision analysis,
  headline) runs only here. Rationale: single officiating regime (post the
  2021 non-basketball-move foul rule), no bubble/COVID seasons.
- **RAPM ingestion window: 2019-20 onward**, with 2019-20 and 2020-21 used
  only as half-life decay burn-in for ratings — never as analysis seasons.
- Windows are enforced by `src/config.py`; no module hardcodes seasons.
- Gate: every included season passes the stint-minutes vs. box-score
  validation gate (per season, logged in VALIDATION.md) before anything
  downstream runs.

## Phase 2 — Robustness window

- HIERARCHICAL_KAPPA_PLAN.md Phases B–D (per-player / tier κ with partial
  pooling; ~1.5 weeks, λ_κ cross-validation is the slow part).
- Sensitivity: RAPM half-life sweep, κ = 0 conservative bound, per-archetype
  policy costs, game-clustered SEs for κ.
- Killer validation chart (model vs constant-hazard foul-out probability).

## Phase 3 — Paper

- Abstract draft by mid-September (Oct 1 deadline, ≥2 weeks buffer);
  HIERARCHICAL_KAPPA_PLAN Phase E claims decision closes before the draft
  starts (Aug 31).
- VALIDATION.md ships with the open-source release.
