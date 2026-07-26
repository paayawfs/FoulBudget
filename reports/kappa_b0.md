# B0 selection check — FORCED vs CHOSEN foul-trouble exposure (5 seasons: 2021–2025)

## Subsample sizes (report these before anything else)
- window 5 min, |d| <= 3: 2,314 FORCED foul-trouble possessions
- final window: last 5 min of regulation (or OT), |d| <= 3, top-half delta48 among rotation players (>= 500 min)
- FORCED: 2,314 possessions (784 spells) | CHOSEN: 79,501 possessions

## Raw split (per 48; naive SEs, difference t ignores covariance)
                      per48  se48     t
foul_trouble[FORCED]  14.11  3.72  3.80
foul_trouble[CHOSEN]   3.93  0.64  6.13
difference FORCED - CHOSEN: +10.18 per 48, t = 2.70

## DiD spec (window main effect included; foul_trouble[FORCED]
## = within-clutch foul-trouble shift — the cleaner number)
                      per48  se48     t
foul_trouble[FORCED]  11.44  3.86  2.97
foul_trouble[CHOSEN]   3.94  0.64  6.15
clutch_window          2.74  1.07  2.57
DiD difference FORCED - CHOSEN: +7.50 per 48, t = 1.92

## Endgame-ritual robustness (final 90s split out; DiD spec)
FORCED-core: 2,010 poss | FORCED-final90: 304 poss
                              per48   se48     t
foul_trouble[FORCED-core]      5.58   4.12  1.36
foul_trouble[FORCED-final90]  50.18  10.29  4.88
foul_trouble[CHOSEN]           3.94   0.64  6.15
clutch_window                  2.74   1.07  2.57

## Foul-rate tier x FORCED/CHOSEN cell sizes (possessions)
CHOSEN|high-foul    38579.0
CHOSEN|low-foul     16700.0
CHOSEN|mid-foul     24222.0
FORCED|high-foul     1212.0
FORCED|low-foul       382.0
FORCED|mid-foul       720.0
tier split SKIPPED: smallest FORCED cell 382 < 500 possessions

## Interpretation
Decision rule (logged verbatim per HIERARCHICAL_KAPPA_PLAN Phase B0, no
thumb on the scale):
- If FORCED kappa-bar remains significantly positive: adaptation is real;
  the estimated-kappa headline (2.05 wins) stands with this as its
  identification defense.
- If FORCED kappa-bar is ~0 or negative: the positive pooled kappa is
  substantially selection; the defensible headline shifts toward the
  kappa=0 floor (0.65 wins), and paper language must change. Flag every
  downstream artifact this touches (headline table, per-player cost
  tables, top-20 lists).

Known confound either way: FORCED minutes are high-leverage end-game
minutes, so intensity/effort differs from average minutes independent of
foul trouble. The DiD spec (window main effect included; the
foul_trouble[FORCED] coefficient is then the within-clutch foul-trouble
shift) mitigates this and is the cleaner number.

VERDICT: AMBIGUOUS — the raw and DiD specs do not agree (or FORCED kappa-bar is positive but not significant). Stop and review before changing any paper language.

## Widened rerun — pre-registered protocol (2026-07-24, registered BEFORE running)

The 2026-07-18 run above landed ambiguous: the endgame-ritual contamination
check showed the final 90 seconds (take fouls, FT contests, trailing-team
gambles) carry most of the FORCED signal, and the stripped core was positive
but underpowered (+5.58/48, t = 1.4, 2,010 poss). The rerun below widens the
window to recover power while ALWAYS excluding that contaminated stretch.
Protocol and stopping rule are fixed here before any code runs.

**Rung 1:** FORCED = spells starting in the final 7.0 minutes of regulation
(or any OT), |d| <= 6, player's delta48 in the top half of rotation players
(>= 500 min) that season, ALWAYS excluding spells starting in the final 90
seconds of regulation/OT while within one possession (|d| <= 3) — the exact
exclusion definition from the endgame-ritual contamination check above.
Excluded spells form their own regression cell (as in the contamination
check); they contaminate neither FORCED nor CHOSEN.

**Rung 2** (run only if rung 1 is ambiguous AND its point estimate is still
positive): extend the window to the final 9.0 minutes; same margin, same
exclusion, nothing else changes.

**STOPPING RULE:** after rung 2 the result stands as-is. No third widening,
no cutoff adjustment, no alternative specifications. If it is ambiguous
after rung 2, the verdict is "underpowered, not contradicted" permanently.

**Decision thresholds (pre-registered, applied to the DiD spec):**
- "defended" = FORCED-core kappa-bar positive with t >= 2 in the DiD spec
- "ambiguous" = positive but t < 2
- "selection-driven" = point estimate at or below zero

Same spell-WLS machinery and DiD spec as above (clutch-window main effect
included; raw split reported alongside). Report subsample sizes at each
rung, point estimates, SEs, t-stats, and which verdict fired.

<!-- widened-results -->

## Widened rerun — results (protocol above, registered before running)

### Rung 1: final 7 min, |d| <= 6, top-half delta, final-90s one-possession spells excluded
FORCED: 7,781 poss (1,514 spells) | EXCLUDED-final90: 353 poss | CHOSEN: 77,016 poss

raw split (per 48; naive SEs, difference t ignores covariance):
                                per48  se48     t
foul_trouble[FORCED]             0.21  2.04  0.10
foul_trouble[EXCLUDED-final90]  53.95  9.50  5.68
foul_trouble[CHOSEN]             4.13  0.65  6.33
difference FORCED - CHOSEN: -3.92 per 48, t = -1.83

DiD spec (window main effect included; foul_trouble[FORCED] = within-clutch foul-trouble shift — the verdict number):
                                per48  se48     t
foul_trouble[FORCED]            -1.96  2.11 -0.93
foul_trouble[EXCLUDED-final90]  51.64  9.51  5.43
foul_trouble[CHOSEN]             4.19  0.65  6.43
clutch_window                    2.74  0.64  4.31
DiD difference FORCED - CHOSEN: -6.16 per 48, t = -2.79

VERDICT (pre-registered threshold): SELECTION-DRIVEN — FORCED-core point estimate at or below zero. The positive pooled kappa is substantially selection; the kappa-boosted numbers are not causally defensible. Downstream artifacts flagged: headline table, E6 per-player tables, E7 team slice, kappa_share column.
