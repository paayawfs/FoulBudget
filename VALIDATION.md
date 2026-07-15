# VALIDATION.md — verification suite results

Run: `python tests/run_validation.py` (regenerates this file).

kappa convention: TEST_CASES.md's multiplicative 'kappa = 1 (no discount)'
maps to this model's additive kappa = 0; 'strong discount' maps to
kappa negative enough that delta + kappa < 0 in foul trouble.

| test | status | summary |
|---|---|---|
| A1/D2 | PASS | kappa_add=0, constant-leverage terminal: sit-states = 0 (expect 0; Weinstein's truncation argument assumes leverage-flat value) |
| A1.option-value | INFO | same player under real W(d,t): 0 sit-states -- even leverage variation does not justify benching at kappa=0 given the adaptive hazard (pre-fix sits were boundary artifacts) |
| A2 | PASS | delta=0: max |V_opt - V_conv| over lattice = 6.66e-16 (expect ~0) |
| A3 | PASS | lambda=0: sit-states = 0 (expect 0) |
| A4/D1 | PASS | kappa_add=-0.25 (trouble-delta < 0): sit-states = 14530, agreement with Q+1 inside trouble region = 98% (Maymin-style benching is a special case at a kappa the data rejects) |
| A5.lam | PASS | sit-states over lam grid [0.02, 0.05, 0.08, 0.11, 0.14]: [0, 0, 0, 0, 0] (expect more sits) |
| A5.kappa | PASS | sit-states over kappa grid [-0.2, -0.1, 0.0, 0.083]: [14527, 8784, 0, 0] (expect fewer sits) |
| A5.delta | PASS | sit-states over delta grid: [0, 0, 0, 0, 0]; sits at |d|<10 (must be 0): [0, 0, 0, 0, 0] (rising total = option value in blowout states, inspected and expected) |
| B1 | PASS | delta=+1/48, t<=120s: sit-states = 0 (expect 0) |
| B2 | PASS | max |V(f=6)| difference across delta=0 vs 0.20: 0.00e+00 (expect 0 -- absorbing) |
| B3 | PASS | max convention cost at |d|>=28 with <=12 min left: 0.069pp (expect ~0; over all t it is 5.12pp -- early 28-point deficits are ~1.6 sigma from even, not saturated) |
| B4 | PASS | max |W(d)+W(-d)-1| on lattice: 0.0014 (tolerance 0.03; steps de-meaned, residual skew only) |
| C1 | PASS | max |sum(weights) - 1| over player-seasons: 2.00e-15 |
| C2 | PASS | negative WP costs among 2,144 occurrences: 0 (min = 0.00e+00) |
| C3 | N/A | v1 estimates a single pooled kappa (+3.99/48); the hierarchical per-player version is a planned refinement, test activates then |
| C4 | PASS | aggregate predicted/actual fouls = 1.0142 (within 2%), per-player-season corr = 0.997 (>=50 fouls; per-player gaps are the shrinkage prior working) |
| C5 | PENDING | requires nbarapm.com same-window values (external download); run when the comparison file is available |
| E1 | EYEBALL | top-12 by mean WP cost per occurrence (>=5 occurrences): |
| E2 | PASS | corr(model lambda, raw per-36 fouls) = 0.999 (>=1000 min, 2024) |
| E3 | EYEBALL | stars with strongest backups (delta should compress): |
| E4 | EYEBALL | case studies: top-decile-delta starters benched >=6 min after Q+1 trouble in games decided by <=5: |
| E5 | EYEBALL | game 22400475, Nikola Jokić (delta +9.2/48, lam 2.0/36) |

## Artifacts
### E1 (EYEBALL)
```
top-12 by mean WP cost per occurrence (>=5 occurrences):
                   name  mean_pp  count  delta48
           Franz Wagner     5.40     12     5.58
            Paul George     5.05      6     3.15
           Nikola Jokić     5.00     10     9.18
  Giannis Antetokounmpo     4.93     11     6.95
         Toumani Camara     4.63     21     3.22
       Dereck Lively II     4.53      5     2.57
Shai Gilgeous-Alexander     4.25     13     6.81
          Jarrett Allen     4.09      9     0.85
         Walker Kessler     3.95      9     1.48
    Dorian Finney-Smith     3.84     12     5.04
          Javonte Green     3.81      6     1.08
      Bogdan Bogdanović     3.80      6     1.01
```

### E2 (PASS)
```
corr(model lambda, raw per-36 fouls) = 0.999 (>=1000 min, 2024)
highest lambda:
           name  lam36  per36
Donovan Clingan   4.26   5.15
   Kevon Looney   3.97   4.84
      Zach Edey   3.82   4.57
 Isaiah Stewart   3.80   4.56
    Jalen Duren   3.75   4.42
lowest lambda:
             name  lam36  per36
       Tyus Jones   0.99   1.04
      Tyler Herro   1.03   1.12
     Jimmy Butler   1.05   1.07
  Harrison Barnes   1.13   1.21
Tyrese Haliburton   1.23   1.35
```

### E3 (EYEBALL)
```
stars with strongest backups (delta should compress):
              name  rapm48  comp48  delta48
    Jalen Williams   -0.15    3.83    -3.98
Isaiah Hartenstein    4.69    2.78     1.91
     Aaron Wiggins    2.05    2.67    -0.61
    Darius Garland    2.43    2.63    -0.20
     Cason Wallace   -0.22    2.55    -2.77
weakest backups (delta should stretch):
          name  rapm48  comp48  delta48
Kyshawn George    0.17   -1.98     2.15
  Jordan Poole   -1.96   -1.98     0.01
 Corey Kispert   -1.74   -1.87     0.13
 Collin Sexton   -0.92   -1.80     0.89
Keyonte George   -4.11   -1.42    -2.68
```

### E4 (EYEBALL)
```
case studies: top-decile-delta starters benched >=6 min after Q+1 trouble in games decided by <=5:
 game_id                  name  period  foul_count  sat  remaining  final_margin  delta48
22400475          Nikola Jokić       1           2 11.4       43.7           3.0      9.2
22400799 Giannis Antetokounmpo       1           2 28.7       42.7           3.0      6.9
22400526 Giannis Antetokounmpo       1           2 11.5       39.2           3.0      6.9
```

### E5 (EYEBALL)
```
game 22400475, Nikola Jokić (delta +9.2/48, lam 2.0/36)
  Q1  48.0m left | d= +0 | f=0         | coach: on  1.4m (foul) | model: play
  Q1  46.4m left | d= +2 | f=1         | coach: on  2.8m (foul) | model: play
  Q1  43.7m left | d= -9 | f=2 TROUBLE | coach: on  4.2m (sub_out) | model: play
  Q2  32.4m left | d=-10 | f=2         | coach: on  8.3m (sub_out) | model: play
  Q3  24.0m left | d= -8 | f=2         | coach: on 12.0m (period_end) | model: play
  Q4   7.9m left | d= -5 | f=2         | coach: on  0.9m (foul) | model: play
  Q4   7.0m left | d= -2 | f=3         | coach: on  7.0m (game_end) | model: play
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
