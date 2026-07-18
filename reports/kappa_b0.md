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