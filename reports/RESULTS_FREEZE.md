# RESULTS_FREEZE.md — definitive numbers for the abstract and paper

Frozen 2026-07-24 at tag `results-freeze-v1`. Validation suite: 27 checks,
0 FAIL. Nothing below changes without unfreezing, and any unfreeze must be
logged here.

## Headline (verdict-dependent framing, B0 = selection-driven)

**Conventional foul-trouble benching costs at least 0.65 wins per team per
season (0.80 percentage points of win probability per occurrence). This
floor is computed at kappa = 0 and is the paper's causal claim.**

The larger figure of 2.05 wins per team per season (2.54pp per occurrence)
uses the estimated kappa and, per the pre-registered B0 selection check,
is *descriptive accounting of the convention as currently managed*, never
a causal claim. The B0 verdict is final under its pre-registered stopping
rule: in FORCED exposure, where coaches have no real benching option
(final 7 minutes, margin within 6, take-foul window excluded, 5,859
possessions), the foul-trouble performance shift is negative, minus 0.59 per 48
(t = negative 0.24), against +4.25 per 48 in CHOSEN exposure. The pooled
kappa is coach selection, not player adaptation. Abstract leads with the
floor. (tag `b0-final`)

## Core estimates

| quantity | value | tag |
|---|---|---|
| foul-trouble hazard multiplier (gamma_1, foul-rate adaptation) | x0.641 | `kappa-v2` |
| pooled kappa (performance shift in foul trouble, descriptive) | +4.22 per 48 (t = 6.7) | `kappa-v2` |
| B0 FORCED kappa (DiD, the identification test) | −0.59 per 48 (t = −0.24) | `b0-final` |
| foul-trouble occurrences evaluated (2025-26) | 2,423 | `cost-tables-v1` |
| WP cost per occurrence, kappa = 0 / estimated kappa | 0.80pp / 2.54pp | `cost-tables-v1` |
| wins per team per season, kappa = 0 / estimated kappa | 0.65 / 2.05 | `cost-tables-v1` |

Note the two adaptation channels are distinct and only one survived B0:
the foul-RATE adaptation (players in trouble foul at 0.64x their base
hazard) is estimated on within-player variation and stands; the
performance kappa does not survive forced exposure and is descriptive.

## Player and team slices (E6/E7, tag `cost-tables-v1`, re-labeled at `b0-final`)

Defensible numbers are the kappa = 0 columns (total_pp_k0, wins_k0).
- Largest defensible season cost: N. Jokić, 37.7pp total at kappa = 0
  (63.1pp as-managed, 18 occurrences).
- V. Wembanyama: 31.9pp at kappa = 0 (60.9pp as-managed, 14 occurrences,
  4.35pp per occurrence as-managed).
- Cautionary relabel: D. Brooks tops the as-managed table (112.2pp) but
  94% of it is the kappa boost; his defensible total is 6.9pp.
- Cheapest occurrences: J. McDaniels (0.50pp per occurrence as-managed,
  0.26pp season total at kappa = 0) and J. Huff (0.87pp; 0.94pp at k0):
  benching a low-delta player costs roughly nothing, which is the
  convention working as intended at the bottom of the rotation.
- Team extremes (2025-26): PHX loses most (3.65 wins as-managed, 0.91 at
  kappa = 0); IND least (0.94 / 0.33).

## Opponent-strength robustness (E8, tag `e8-opponent-split`): PASS

Mean cost per occurrence at kappa = 0 by opponent team-season net-rating
tercile: strong 0.79pp, average 0.81pp, weak 0.80pp. The cost is flat in
opponent strength; the floor is not an artifact of blowout or weak-opponent
states. The secondary on-floor lineup RAPM split shows the same pattern.

## The one-sentence framing the abstract uses

Conventional foul-trouble benching costs NBA teams at least 0.65 wins per
team per season even under the most conservative assumption that players
perform no differently in foul trouble, and the widely feared
playing-scared effect does not appear where coaches are forced to test it.
