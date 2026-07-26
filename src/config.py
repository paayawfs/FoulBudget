"""Season windows per REFERENCE.md Section 4 two-window design (2026-07-14).

Single source of truth -- no module hardcodes a season list, so the pipeline
cannot ingest by accident what the design excludes on purpose.

Season numbering follows shufinskiy/nba_data: 2021 = the 2021-22 season.
"""

import numpy as np

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

# Foul-trouble threshold per REFERENCE.md Section 3.4 -- single source of
# truth so kappa estimation, the hazard robustness specs, the B0 selection
# check, the DP's conventional policy, and occurrence selection for the
# headline all apply the identical rule; no module re-derives it.
#
# Regulation (period 1-4): quarter + 1. Overtime (period >= 5): capped at
# FOUL_OUT - 1 = 5, since foul_count >= 6 is disqualification and could
# structurally never be reached by a player still on the floor under a
# literal period + 1 formula (period 5 would require 6 fouls). period + 1
# already equals 5 at period 4, so min(period + 1, FOUL_OUT - 1) is one
# formula that is exact in both regulation and overtime -- no special case.
FOUL_OUT = 6


def foul_trouble_threshold(period):
    """Fouls needed to count as foul trouble, given period (scalar or array)."""
    return np.minimum(period + 1, FOUL_OUT - 1)
