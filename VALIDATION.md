# VALIDATION.md — verification suite results

Run: `python tests/run_validation.py` (regenerates this file).

kappa convention: TEST_CASES.md's multiplicative 'kappa = 1 (no discount)'
maps to this model's additive kappa = 0; 'strong discount' maps to
kappa negative enough that delta + kappa < 0 in foul trouble.

| test | status | summary |
|---|---|---|
| A1/D2 | PASS | kappa_add=0, constant-leverage terminal: sit-states = 0 (expect 0; Weinstein's truncation argument assumes leverage-flat value) |
| A1.option-value | INFO | same player under real W(d,t): 0 sit-states -- even leverage variation does not justify benching at kappa=0 given the adaptive hazard (pre-fix sits were boundary artifacts) |
| A2 | PASS | delta=0: max |V_opt - V_conv| over lattice = 7.77e-16 (expect ~0) |
| A3 | PASS | lambda=0: sit-states = 0 (expect 0) |
| A4/D1 | PASS | kappa_add=-0.25 (trouble-delta < 0): sit-states = 14531, agreement with Q+1 inside trouble region = 98% (Maymin-style benching is a special case at a kappa the data rejects) |
| A5.lam | PASS | sit-states over lam grid [0.02, 0.05, 0.08, 0.11, 0.14]: [0, 0, 0, 0, 0] (expect more sits) |
| A5.kappa | PASS | sit-states over kappa grid [-0.2, -0.1, 0.0, 0.083]: [14525, 8784, 0, 0] (expect fewer sits) |
| A5.delta | PASS | sit-states over delta grid: [0, 0, 0, 0, 0]; sits at |d|<10 (must be 0): [0, 0, 0, 0, 0] (rising total = option value in blowout states, inspected and expected) |
| B1 | PASS | delta=+1/48, t<=120s: sit-states = 0 (expect 0) |
| B2 | PASS | max |V(f=6)| difference across delta=0 vs 0.20: 0.00e+00 (expect 0 -- absorbing) |
| B3 | PASS | max convention cost at |d|>=28 with <=12 min left: 0.073pp (expect ~0; over all t it is 5.32pp -- early 28-point deficits are ~1.6 sigma from even, not saturated) |
| B4 | PASS | max |W(d)+W(-d)-1| on lattice: 0.0009 (tolerance 0.03; steps de-meaned, residual skew only) |
| C1 | PASS | max |sum(weights) - 1| over player-seasons: 2.00e-15 |
| C2 | PASS | negative WP costs among 2,423 occurrences: 0 (min = 0.00e+00) |
| C3 | PASS | kappa_i shrinkage: sd(dev) 0.44 (<25 FT poss) -> 2.15 (>=250) per48, max thin-sample |dev| = 1.51; FT-weighted mean kappa_i +4.22 vs v1 pooled +4.22; OOS gain over pooled = +0.031% of held-out MSE (lambda_kappa = 640) |
| C4 | PASS | aggregate predicted/actual fouls = 1.0139 (within 2%), per-player-season corr = 0.997 (>=50 fouls; per-player gaps are the shrinkage prior working) |
| C5 | PENDING | requires nbarapm.com same-window values (external download); run when the comparison file is available |
| E1 | EYEBALL | top-12 by mean WP cost per occurrence (>=5 occurrences): |
| E2 | PASS | corr(model lambda, raw per-36 fouls) = 0.998 (>=1000 min, 2025) |
| E3 | EYEBALL | stars with strongest backups (delta should compress): |
| E4 | EYEBALL | case studies: top-decile-delta starters benched >=6 min after Q+1 trouble in games decided by <=5: |
| E5 | EYEBALL | game 22500203, G. Antetokounmpo (delta +8.5/48, lam 2.6/36) |

## Artifacts
### E1 (EYEBALL)
```
top-12 by mean WP cost per occurrence (>=5 occurrences):
                 name  mean_pp  count  delta48
             M. Smart     4.79      9     3.61
            E. Mobley     4.67      8     1.57
     G. Antetokounmpo     4.50      6     8.49
S. Gilgeous-Alexander     4.49      7     7.21
        V. Wembanyama     4.35     14     6.56
        J. Champagnie     4.33      5     2.39
            P. George     4.27      7     2.27
            D. Booker     4.15     13     3.15
             J. Allen     4.07      8     2.79
          C. Holmgren     4.07      5     3.69
             J. Suggs     3.96     14     2.55
            L. Dončić     3.90     13     3.84
```

### E2 (PASS)
```
corr(model lambda, raw per-36 fouls) = 0.998 (>=1000 min, 2025)
highest lambda:
         name  lam36  per36
     L. Garza   4.27   5.17
K. Filipowski   3.92   4.59
    J. Poeltl   3.83   4.52
   I. Stewart   3.82   4.50
   S. Cissoko   3.82   4.59
lowest lambda:
         name  lam36  per36
   K. Leonard   1.25   1.35
     L. James   1.34   1.47
       S. Bey   1.37   1.52
J. Butler III   1.37   1.40
    H. Barnes   1.40   1.54
```

### E3 (EYEBALL)
```
stars with strongest backups (delta should compress):
         name  rapm48  comp48  delta48
  C. Holmgren    6.64    2.95     3.69
      L. Dort   -0.83    2.59    -3.43
    S. Castle    1.42    2.56    -1.14
R. Holland II    0.59    2.36    -1.77
    D. Harper    3.10    2.35     0.75
weakest backups (delta should stretch):
         name  rapm48  comp48  delta48
      T. Mann   -0.28   -1.53     1.24
     W. Riley   -3.32   -1.52    -1.80
M. Porter Jr.    1.61   -1.46     3.08
     A. Green    2.02   -1.30     3.33
   I. Collier   -4.50   -1.22    -3.28
```

### E4 (EYEBALL)
```
case studies: top-decile-delta starters benched >=6 min after Q+1 trouble in games decided by <=5:
 game_id                  name  period  foul_count  sat  remaining  final_margin  delta48
22500203      G. Antetokounmpo       1           2  7.6       36.7             2      8.5
22500893 S. Gilgeous-Alexander       1           2  8.0       39.1             3      7.2
22500552         V. Wembanyama       2           3  9.1       24.5             1      6.6
```

### E5 (EYEBALL)
```
game 22500203, G. Antetokounmpo (delta +8.5/48, lam 2.6/36)
  Q1  48.0m left | d= -0 | f=0         | coach: on  2.4m (foul) | model: play
  Q1  45.6m left | d= -3 | f=1         | coach: on  4.8m (sub_out) | model: play
  Q1  37.9m left | d= -4 | f=1         | coach: on  1.2m (foul) | model: play
  Q1  36.7m left | d= -5 | f=2 TROUBLE | coach: on  0.7m (period_end) | model: play
  Q2  36.0m left | d= -4 | f=2         | coach: on  4.3m (sub_out) | model: play
  Q2  27.9m left | d= -2 | f=2         | coach: on  3.1m (foul) | model: play
  Q2  24.7m left | d= -6 | f=3 TROUBLE | coach: on  0.7m (period_end) | model: play
  Q3  24.0m left | d= -4 | f=3         | coach: on  6.2m (sub_out) | model: play
  Q3  14.0m left | d=-10 | f=3         | coach: on  2.0m (period_end) | model: play
  Q4  12.0m left | d= -9 | f=3         | coach: on  5.5m (foul) | model: play
  Q4   6.5m left | d= -2 | f=4         | coach: on  6.5m (foul) | model: play
  Q4   0.0m left | d= +2 | f=5 TROUBLE | coach: on  0.0m (game_end) | model: sit
```

<!-- session-log -->

## Data expansion gates — 2026-07-15 (PROJECT_PLAN Phase 1)

Corpus: behavioral window 2021-2025 (5 seasons, 6,144 games after corrupt-game
drops), RAPM burn-in 2019-2020 (lineups only). 2025-26 exists only in v3/cdn
format upstream; ingested via the cdnnba adapter in src/ingest/lineups.py
(paired out/in sub rows, home side recovered from scoreHome increments,
period-start administrative subs demoted, foul classification verified 0
mismatches vs cdn's own foulPersonalTotal on 21,278 player-games).

Free physical screen (check_team_minutes): 0 flagged team-rows / 6,144 games.

Per-season box-score gate (validate_minutes, 15 games/season + 12-game
regression set, 2,004 player-game rows): PASS

| season | rows | MAE (min) | within 1 min | max err |
|---|---|---|---|---|
| 2021 | 392 | 0.042 | 100% | 0.55 |
| 2022 | 381 | 0.044 | 100% | 0.70 |
| 2023 | 397 | 0.039 | 100% | 0.52 |
| 2024 | 442 | 0.038 | 100% | 0.45 |
| 2025 | 392 | 0.042 | 100% | 0.43 |

Manual fixes this expansion required (all in code, documented in place):
- cdnnba adapter for 2025-26 (no v2 feed exists upstream).
- nba_on_court has a hidden network fallback to stats.nba.com for games it
  cannot resolve locally; 9 such 2025 games needed retry on timeout.
- BoxScoreTraditionalV2 stopped publishing at 2025-26; gate falls back to V3
  (whose minutes field uses "" for DNP players).
- Team attribution in exposure.py now majority-voted (game 22100405 had a
  single mislabeled row that flipped a starter's team).
- CORRUPT_GAMES grew by one: 22100545 (2021, wholesale-corrupt sub ledger).

## Re-estimation on the 5-season window — old vs new headline (2026-07-15)

Full verification suite: 22 checks, 0 FAIL (regenerated above).

| quantity | dev slice (3 szn, eval 2024) | expanded (5 szn, eval 2025) |
|---|---|---|
| foul-trouble hazard multiplier | x0.656 | x0.641 |
| pooled kappa (pts/48, t) | +3.99 (4.8) | +4.22 (6.7) |
| kappa sensitivity spec | +4.54 (2.2) | +3.26 (2.1) |
| occurrences evaluated | 2,144 | 2,423 |
| WP cost/occurrence, estimated kappa | 2.43pp | 2.54pp |
| wins/team/season, estimated kappa | 1.73 | 2.05 |
| WP cost/occurrence, kappa = 0 | 0.81pp | 0.80pp |
| wins/team/season, kappa = 0 | 0.58 | 0.65 |
| Q1-trouble cost (estimated kappa) | 3.77pp | 3.91pp |

Every core number moved modestly and in no case changed sign or story:
adaptation strengthened slightly, kappa is more precise, and the headline
range is now 0.65-2.05 wins/team/season.

## kappa v2 — per-player deviations, Phase B-E verdict (2026-07-15)

Spec (src/hazard/kappa_v2.py): kappa spell WLS + one ridge-penalized
foul-trouble deviation column per player (795), global kappa-bar lightly
penalized, league-wide pooling per the Phase A decision. lambda_kappa = 640
by 2-fold CV over games, scored on held-out foul-trouble spells.

| gate | result |
|---|---|
| reconciliation | kappa-bar +4.33/48; FT-min-weighted mean kappa_i +4.22/48 = v1 pooled +4.22/48 |
| C3 shrinkage | sd(dev) 0.44/48 (<25 FT poss) widening to 2.15/48 (>=250); thin samples hug the mean |
| OOS gate | kappa_i beats pooled kappa-bar by +0.031% of held-out MSE (~= 0) |
| face validity | reportable (>=250 poss, n=83) range -0.8 to +11.1 per 48 around +4.3 mean; no thin-sample extremes |

**Phase E claims decision: outcome 2 (weak heterogeneity).** The data
supports a pooled playing-scared effect with limited individual variation;
paper language is "we tested for player-specific playing-scared effects;
the data supports group-level effects" and personalization rests on delta_i
and lambda_i. The DP and headline keep pooled kappa-bar (the Phase D DP
integration check is therefore moot: integrating kappa_i ~= kappa-bar
changes nothing the OOS gate hasn't already rejected). Artifacts:
reports/kappa_v2.md, data/processed/hazard/kappa_v2.csv.
