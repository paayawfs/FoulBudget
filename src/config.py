"""Season windows per REFERENCE.md Section 4 two-window design (2026-07-14).

Single source of truth -- no module hardcodes a season list, so the pipeline
cannot ingest by accident what the design excludes on purpose.

Season numbering follows shufinskiy/nba_data: 2021 = the 2021-22 season.
"""

# behavioral analysis window: kappa, lambda, hazard, DP, decision analysis,
# headline, W(d,t). One officiating regime, no bubble/COVID seasons.
ANALYSIS_SEASONS = (2021, 2022, 2023, 2024, 2025)

# decay burn-in for RAPM only: stints feed the half-life ridge, but these
# seasons get no reported ratings and are never analysis seasons.
BURNIN_SEASONS = (2019, 2020)

RAPM_SEASONS = BURNIN_SEASONS + ANALYSIS_SEASONS

# newest complete analysis season: policy-cost evaluation states come from
# here; 2024 kept alongside in comparisons for continuity with the dev slice.
EVAL_SEASON = 2025
