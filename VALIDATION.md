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
| B3 | PASS | max convention cost at |d|>=28 with <=12 min left: 0.071pp (expect ~0; over all t it is 5.12pp -- early 28-point deficits are ~1.6 sigma from even, not saturated) |
| B4 | PASS | max |W(d)+W(-d)-1| on lattice: 0.0009 (tolerance 0.03; steps de-meaned, residual skew only) |
| B0 | EYEBALL | B0-final rung 1: FORCED (last 7 min, |d|<=6, top-half delta, final-90s one-possession spells excluded) DiD kappa-bar -1.96/48 (t=-0.9), raw +0.21/48 (t=0.1) vs CHOSEN +4.19/48 on 7,781 FORCED poss; excluded ritual cell +51.64/48 (353 poss); verdict: selection-driven — estimated-kappa numbers are descriptive, the kappa=0 floor is the causal claim (reports/kappa_b0.md) |
| C1 | PASS | max |sum(weights) - 1| over player-seasons: 2.00e-15 |
| C2 | PASS | negative WP costs among 2,485 occurrences: 0 (min = 0.00e+00) |
| C3 | PASS | kappa_i shrinkage: sd(dev) 0.44 (<25 FT poss) -> 2.13 (>=250) per48, max thin-sample |dev| = 1.78; FT-weighted mean kappa_i +3.98 vs v1 pooled +3.98; OOS gain over pooled = +0.029% of held-out MSE (lambda_kappa = 640) |
| C4 | PASS | aggregate predicted/actual fouls = 1.0139 (within 2%), per-player-season corr = 0.997 (>=50 fouls; per-player gaps are the shrinkage prior working) |
| C5 | PASS | in-house 2025 decayed RAPM vs nbarapm.com (n=279, >=1000 min): r = 0.962 vs their time-decay RAPM (gate 0.9); 3y 0.943, 5y 0.922, 1y 0.876 -- decay ordering as expected |
| E1 | EYEBALL | top-12 by mean WP cost per occurrence (>=5 occurrences): |
| E2 | PASS | corr(model lambda, raw per-36 fouls) = 0.998 (>=1000 min, 2025) |
| E3 | EYEBALL | stars with strongest backups (delta should compress): |
| E4 | EYEBALL | case studies: top-decile-delta starters benched >=6 min after Q+1 trouble in games decided by <=5: |
| E5 | EYEBALL | game 22500203, G. Antetokounmpo (delta +8.5/48, lam 2.6/36) |
| E6 | EYEBALL | per-player WP cost of convention (2025, >=5 occurrences, n = 216; B0 verdict selection-driven: mean_pp/total_pp (kappa=0) are the PRIMARY, causally defensible ranking; mean_pp_est/total_pp_est are the non-defensible as-managed appendix per player): |
| E7 | EYEBALL | wins lost per season to the convention by team (2025; B0 verdict selection-driven: wins (kappa=0) is the PRIMARY, causally defensible ranking, sorted descending; wins_est is the non-defensible as-managed appendix; occurrences located at the team they happened for, traded players split): |
| E8-A | PASS | opponent team-season net-rating terciles (2,485 occurrences): strong n=749 est 2.32pp k0 0.76pp | average n=871 est 2.36pp k0 0.79pp | weak n=865 est 2.39pp k0 0.78pp (pass condition: k0 positive in every tercile; reports/e8_opponent_split.md) |
| E8-B | EYEBALL | opponent on-floor lineup RAPM terciles (secondary, correlates with score state; match rate 100.0%): strong n=828 est 2.31pp k0 0.73pp | average n=828 est 2.41pp k0 0.82pp | weak n=829 est 2.35pp k0 0.79pp |

## Artifacts
### E1 (EYEBALL)
```
top-12 by mean WP cost per occurrence (>=5 occurrences):
                 name  mean_pp  count  delta48
             M. Smart     4.63      9     3.61
            E. Mobley     4.45      8     1.57
     G. Antetokounmpo     4.40      6     8.49
S. Gilgeous-Alexander     4.38      7     7.21
        V. Wembanyama     4.23     14     6.56
        J. Champagnie     4.15      5     2.39
            D. Booker     4.00     13     3.15
             J. Allen     3.92      8     2.79
             J. Suggs     3.79     14     2.55
            L. Dončić     3.76     13     3.84
          O. Ighodaro     3.70     19     2.25
             S. Curry     3.69      5     2.58
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
  Q4   0.0m left | d= +2 | f=5 TROUBLE | coach: on  0.0m (game_end) | model: --
```

### E6 (EYEBALL)
```
per-player WP cost of convention (2025, >=5 occurrences, n = 216; B0 verdict selection-driven: mean_pp/total_pp (kappa=0) are the PRIMARY, causally defensible ranking; mean_pp_est/total_pp_est are the non-defensible as-managed appendix per player):
top 20 by per occurrence (mean_pp, kappa=0):
                 name  mean_pp  total_pp  mean_pp_est  total_pp_est  kappa_share  count  delta48
     G. Antetokounmpo     2.60     15.63         4.40         26.38         0.41      6     8.49
S. Gilgeous-Alexander     2.44     17.10         4.38         30.66         0.44      7     7.21
            C. Bryant     2.44     17.07         2.93         20.51         0.17      7    -3.36
            A. Simons     2.29     13.73         2.55         15.28         0.10      6    -2.66
        V. Wembanyama     2.28     31.90         4.23         59.25         0.46     14     6.56
            D. Powell     2.27     13.65         2.75         16.52         0.17      6    -4.17
           I. Collier     2.16     25.87         2.80         33.62         0.23     12    -3.28
             N. Jokić     1.99     37.73         3.25         61.73         0.39     19     8.37
          R. Sheppard     1.94     15.55         2.11         16.88         0.08      8    -3.28
          M. Williams     1.84     14.73         2.44         19.50         0.24      8    -3.43
             M. Smart     1.82     16.42         4.63         41.65         0.61      9     3.61
          N. Richards     1.81     10.88         2.52         15.12         0.28      6    -3.98
            K. George     1.81     14.48         2.34         18.70         0.23      8    -3.25
              G. Dick     1.74     15.66         2.34         21.04         0.26      9    -1.88
        B. Carrington     1.67     23.41         2.15         30.11         0.22     14    -4.76
              J. Sims     1.63     14.67         2.26         20.37         0.28      9    -2.42
           T. Watford     1.63      9.76         2.01         12.09         0.19      6    -2.70
          C. Williams     1.62     11.35         2.30         16.10         0.29      7    -3.71
           J. LaRavia     1.61     30.53         2.49         47.38         0.36     19    -1.92
              R. Dunn     1.60     11.22         2.65         18.58         0.40      7    -1.90
bottom 20 by per occurrence (mean_pp, kappa=0):
          name  mean_pp  total_pp  mean_pp_est  total_pp_est  kappa_share  count  delta48
  T. Hendricks    -0.00     -0.00         3.04         24.32         1.00      8    -0.06
    D. Clingan    -0.00     -0.00         2.04         18.35         1.00      9    -0.12
      K. Ellis    -0.00     -0.00         1.87         14.99         1.00      8     0.13
     N. Traore    -0.00     -0.00         2.18         21.85         1.00     10     0.18
  P. Pritchard    -0.00     -0.00         2.01         10.07         1.00      5    -0.22
    M. Bridges     0.00      0.00         1.21          6.06         1.00      5     0.12
W. Clayton Jr.     0.00      0.00         2.14         17.12         1.00      8    -0.04
      J. Wells     0.00      0.00         3.24         38.85         1.00     12     0.07
     J. Randle     0.00      0.00         0.92          4.59         1.00      5    -0.23
     J. Walker     0.00      0.00         2.87         22.99         1.00      8    -0.06
 K. Jakučionis     0.00      0.00         2.54         20.33         1.00      8     0.07
     J. Harden     0.00      0.00         1.10          5.52         1.00      5     0.01
   J. Williams     0.00      0.00         2.62         23.58         1.00      9    -0.17
       D. Wolf     0.00      0.00         3.24         25.94         1.00      8     0.09
   K. Matković     0.00      0.00         2.97         20.78         1.00      7    -0.23
 M. Bagley III     0.00      0.00         2.95         23.59         1.00      8     0.15
  J. McDaniels     0.02      0.26         0.40          5.18         0.95     13    -0.61
      M. Peavy     0.06      0.38         0.87          5.23         0.93      6     0.71
       J. Huff     0.09      0.94         0.81          8.96         0.90     11    -0.68
   A. Mitchell     0.10      0.48         1.24          6.18         0.92      5     0.40
top 20 by season total (total_pp, kappa=0):
                 name  mean_pp  total_pp  mean_pp_est  total_pp_est  kappa_share  count  delta48
             N. Jokić     1.99     37.73         3.25         61.73         0.39     19     8.37
        V. Wembanyama     2.28     31.90         4.23         59.25         0.46     14     6.56
           J. LaRavia     1.61     30.53         2.49         47.38         0.36     19    -1.92
           I. Collier     2.16     25.87         2.80         33.62         0.23     12    -3.28
        R. Holland II     1.33     25.29         2.03         38.52         0.34     19    -1.77
            A. Bailey     1.38     24.87         2.00         36.01         0.31     18    -1.74
              D. Bane     1.15     24.22         3.33         70.01         0.65     21     3.26
        B. Carrington     1.67     23.41         2.15         30.11         0.22     14    -4.76
             H. Jones     1.25     22.56         3.27         58.92         0.62     18     4.07
           I. Stewart     1.47     22.01         2.18         32.69         0.33     15    -3.82
             A. Black     1.38     20.73         2.27         34.02         0.39     15    -1.82
          O. Ighodaro     1.01     19.21         3.70         70.34         0.73     19     2.25
           J. Mashack     1.59     19.03         3.11         37.26         0.49     12    -1.41
            L. Dončić     1.42     18.46         3.76         48.87         0.62     13     3.84
            D. Booker     1.37     17.75         4.00         51.95         0.66     13     3.15
         J. Smith Jr.     0.98     17.59         1.73         31.20         0.44     18    -1.25
            D. Sharpe     1.24     17.40         3.28         45.93         0.62     14     4.32
S. Gilgeous-Alexander     2.44     17.10         4.38         30.66         0.44      7     7.21
            C. Bryant     2.44     17.07         2.93         20.51         0.17      7    -3.36
          A. Thompson     0.97     16.50         3.15         53.57         0.69     17     2.98
bottom 20 by season total (total_pp, kappa=0):
          name  mean_pp  total_pp  mean_pp_est  total_pp_est  kappa_share  count  delta48
  T. Hendricks    -0.00     -0.00         3.04         24.32         1.00      8    -0.06
    D. Clingan    -0.00     -0.00         2.04         18.35         1.00      9    -0.12
      K. Ellis    -0.00     -0.00         1.87         14.99         1.00      8     0.13
     N. Traore    -0.00     -0.00         2.18         21.85         1.00     10     0.18
  P. Pritchard    -0.00     -0.00         2.01         10.07         1.00      5    -0.22
    M. Bridges     0.00      0.00         1.21          6.06         1.00      5     0.12
W. Clayton Jr.     0.00      0.00         2.14         17.12         1.00      8    -0.04
      J. Wells     0.00      0.00         3.24         38.85         1.00     12     0.07
     J. Randle     0.00      0.00         0.92          4.59         1.00      5    -0.23
     J. Walker     0.00      0.00         2.87         22.99         1.00      8    -0.06
     J. Harden     0.00      0.00         1.10          5.52         1.00      5     0.01
 K. Jakučionis     0.00      0.00         2.54         20.33         1.00      8     0.07
   K. Matković     0.00      0.00         2.97         20.78         1.00      7    -0.23
   J. Williams     0.00      0.00         2.62         23.58         1.00      9    -0.17
       D. Wolf     0.00      0.00         3.24         25.94         1.00      8     0.09
 M. Bagley III     0.00      0.00         2.95         23.59         1.00      8     0.15
  J. McDaniels     0.02      0.26         0.40          5.18         0.95     13    -0.61
      M. Peavy     0.06      0.38         0.87          5.23         0.93      6     0.71
   A. Mitchell     0.10      0.48         1.24          6.18         0.92      5     0.40
      I. Zubac     0.11      0.53         0.65          3.27         0.84      5     1.55
```

### E7 (EYEBALL)
```
wins lost per season to the convention by team (2025; B0 verdict selection-driven: wins (kappa=0) is the PRIMARY, causally defensible ranking, sorted descending; wins_est is the non-defensible as-managed appendix; occurrences located at the team they happened for, traded players split):
team  wins  occurrences  wins_est
 DET  1.22          125      3.16
 UTA  1.22          127      3.26
 ORL  1.03          107      2.88
 LAL  0.98           80      2.24
 DEN  0.95           91      1.94
 PHX  0.91          109      3.47
 WAS  0.83          120      3.08
 BKN  0.78           97      2.53
 SAS  0.78           85      2.14
 MEM  0.77          104      2.73
 BOS  0.74           71      1.60
 CLE  0.74           85      2.18
 OKC  0.69           74      1.90
 MIL  0.67           65      1.55
 NOP  0.64           81      1.91
 PHI  0.64           90      1.91
 POR  0.57           89      1.98
 HOU  0.54           77      1.46
 GSW  0.50           82      2.02
 ATL  0.50           74      1.49
 TOR  0.47           87      1.81
 SAC  0.43           71      1.23
 CHI  0.42           57      1.19
 LAC  0.42           73      1.54
 MIA  0.42           54      1.38
 NYK  0.41           81      1.57
 IND  0.33           54      0.90
 CHA  0.32           49      1.05
 DAL  0.22           62      1.39
 MIN  0.20           64      1.09
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
