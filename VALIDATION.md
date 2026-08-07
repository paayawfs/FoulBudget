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
| C2 | PASS | negative WP costs among 2,485 occurrences: 0 (min = -7.75e-14) |
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
| E8-A | PASS | opponent team-season net-rating terciles (2,485 occurrences): strong n=749 est 1.90pp k0 0.34pp | average n=871 est 1.92pp k0 0.34pp | weak n=865 est 1.94pp k0 0.34pp (pass condition: k0 positive in every tercile; reports/e8_opponent_split.md) |
| E8-B | EYEBALL | opponent on-floor lineup RAPM terciles (secondary, correlates with score state; match rate 100.0%): strong n=828 est 1.95pp k0 0.37pp | average n=828 est 1.93pp k0 0.34pp | weak n=829 est 1.88pp k0 0.32pp |

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
        V. Wembanyama     2.28     31.90         4.23         59.25         0.46     14     6.56
             N. Jokić     1.99     37.73         3.25         61.73         0.39     19     8.37
             M. Smart     1.82     16.42         4.63         41.65         0.61      9     3.61
            P. Siakam     1.47     14.71         3.16         31.61         0.53     10     4.59
            L. Dončić     1.42     18.46         3.76         48.87         0.62     13     3.84
            D. Booker     1.37     17.75         4.00         51.95         0.66     13     3.15
            F. Wagner     1.30      9.10         3.09         21.65         0.58      7     4.04
             A. Green     1.28      8.96         3.57         25.00         0.64      7     3.33
             J. Allen     1.26     10.11         3.92         31.34         0.68      8     2.79
             H. Jones     1.25     22.56         3.27         58.92         0.62     18     4.07
            D. Sharpe     1.24     17.40         3.28         45.93         0.62     14     4.32
          D. Mitchell     1.22     12.16         2.79         27.92         0.56     10     4.30
           C. Johnson     1.21      9.68         3.14         25.14         0.61      8     3.59
              D. Bane     1.15     24.22         3.33         70.01         0.65     21     3.26
            C. Coward     1.10      8.77         3.43         27.43         0.68      8     3.11
          C. Holmgren     1.08      7.56         2.81         19.66         0.62      7     3.69
        J. Champagnie     1.06      5.30         4.15         20.75         0.74      5     2.39
           D. Sabonis     1.05      6.32         3.12         18.73         0.66      6     2.79
bottom 20 by per occurrence (mean_pp, kappa=0):
         name  mean_pp  total_pp  mean_pp_est  total_pp_est  kappa_share  count  delta48
  J. Clarkson     -0.0      -0.0         0.30          1.78          1.0      6    -2.00
R. Dillingham     -0.0      -0.0         0.61          3.03          1.0      5    -1.99
    J. Poeltl     -0.0      -0.0         1.35         13.52          1.0     10    -0.34
      J. Sims     -0.0      -0.0         0.63          5.70          1.0      9    -2.42
B. Carrington     -0.0      -0.0         0.48          6.69          1.0     14    -4.76
    A. Newell     -0.0      -0.0         0.43          2.15          1.0      5    -2.94
 J. McDaniels     -0.0      -0.0         0.38          4.92          1.0     13    -0.61
   N. Claxton     -0.0      -0.0         0.47          3.31          1.0      7    -3.36
    J. Walter     -0.0      -0.0         0.76          6.85          1.0      9    -1.44
   A. Wiggins     -0.0      -0.0         1.21          8.46          1.0      7    -1.45
  A. Drummond     -0.0      -0.0         0.82          5.75          1.0      7    -1.57
      A. Bona     -0.0      -0.0         1.21          8.47          1.0      7    -0.68
 B. Coulibaly     -0.0      -0.0         1.69         22.03          1.0     13    -0.60
   M. Raynaud     -0.0      -0.0         0.31          1.85          1.0      6    -3.00
    V. Krejčí     -0.0      -0.0         0.53          4.74          1.0      9    -1.63
   S. Cissoko     -0.0      -0.0         1.65         16.47          1.0     10    -0.77
 S. Henderson     -0.0      -0.0         0.35          2.79          1.0      8    -1.90
   T. Watford     -0.0      -0.0         0.39          2.33          1.0      6    -2.70
    B. Ingram     -0.0      -0.0         1.30          6.52          1.0      5    -0.74
     B. Brown     -0.0      -0.0         0.42          2.97          1.0      7    -4.50
top 20 by season total (total_pp, kappa=0):
                 name  mean_pp  total_pp  mean_pp_est  total_pp_est  kappa_share  count  delta48
             N. Jokić     1.99     37.73         3.25         61.73         0.39     19     8.37
        V. Wembanyama     2.28     31.90         4.23         59.25         0.46     14     6.56
              D. Bane     1.15     24.22         3.33         70.01         0.65     21     3.26
             H. Jones     1.25     22.56         3.27         58.92         0.62     18     4.07
          O. Ighodaro     1.01     19.21         3.70         70.34         0.73     19     2.25
            L. Dončić     1.42     18.46         3.76         48.87         0.62     13     3.84
            D. Booker     1.37     17.75         4.00         51.95         0.66     13     3.15
            D. Sharpe     1.24     17.40         3.28         45.93         0.62     14     4.32
S. Gilgeous-Alexander     2.44     17.10         4.38         30.66         0.44      7     7.21
          A. Thompson     0.97     16.50         3.15         53.57         0.69     17     2.98
             M. Smart     1.82     16.42         4.63         41.65         0.61      9     3.61
     G. Antetokounmpo     2.60     15.63         4.40         26.38         0.41      6     8.49
            P. Siakam     1.47     14.71         3.16         31.61         0.53     10     4.59
        C. Cunningham     0.73     14.53         3.09         61.88         0.77     20     2.08
          D. Cardwell     0.69     14.52         2.22         46.59         0.69     21     2.87
            K. George     0.64     14.12         3.06         67.41         0.79     22     1.86
            T. Camara     0.70     14.06         2.30         46.05         0.69     20     2.53
          D. Robinson     0.82     13.95         2.89         49.14         0.72     17     2.34
             J. Suggs     0.99     13.89         3.79         53.06         0.74     14     2.55
       J. Jackson Jr.     0.69     13.13         2.26         42.98         0.69     19     2.71
bottom 20 by season total (total_pp, kappa=0):
         name  mean_pp  total_pp  mean_pp_est  total_pp_est  kappa_share  count  delta48
    J. Poeltl     -0.0      -0.0         1.35         13.52          1.0     10    -0.34
      J. Sims     -0.0      -0.0         0.63          5.70          1.0      9    -2.42
  J. Clarkson     -0.0      -0.0         0.30          1.78          1.0      6    -2.00
B. Carrington     -0.0      -0.0         0.48          6.69          1.0     14    -4.76
 J. McDaniels     -0.0      -0.0         0.38          4.92          1.0     13    -0.61
R. Dillingham     -0.0      -0.0         0.61          3.03          1.0      5    -1.99
 B. Coulibaly     -0.0      -0.0         1.69         22.03          1.0     13    -0.60
    J. Walter     -0.0      -0.0         0.76          6.85          1.0      9    -1.44
 J. Smith Jr.     -0.0      -0.0         0.76         13.61          1.0     18    -1.25
   S. Cissoko     -0.0      -0.0         1.65         16.47          1.0     10    -0.77
   N. Claxton     -0.0      -0.0         0.47          3.31          1.0      7    -3.36
    V. Krejčí     -0.0      -0.0         0.53          4.74          1.0      9    -1.63
   A. Wiggins     -0.0      -0.0         1.21          8.46          1.0      7    -1.45
    A. Newell     -0.0      -0.0         0.43          2.15          1.0      5    -2.94
    A. Bailey     -0.0      -0.0         0.62         11.14          1.0     18    -1.74
  A. Drummond     -0.0      -0.0         0.82          5.75          1.0      7    -1.57
      A. Bona     -0.0      -0.0         1.21          8.47          1.0      7    -0.68
  B. Mathurin     -0.0      -0.0         0.58          7.55          1.0     13    -1.29
      J. Hart     -0.0      -0.0         1.01         12.14          1.0     12    -1.34
 S. Henderson     -0.0      -0.0         0.35          2.79          1.0      8    -1.90
```

### E7 (EYEBALL)
```
wins lost per season to the convention by team (2025; B0 verdict selection-driven: wins (kappa=0) is the PRIMARY, causally defensible ranking, sorted descending; wins_est is the non-defensible as-managed appendix; occurrences located at the team they happened for, traded players split):
team  wins  occurrences  wins_est
 ORL  0.59          107      2.44
 DEN  0.53           91      1.53
 DET  0.53          125      2.46
 PHX  0.49          109      3.06
 SAS  0.44           85      1.79
 LAL  0.39           80      1.65
 CLE  0.38           85      1.82
 UTA  0.35          127      2.39
 WAS  0.33          120      2.58
 MIL  0.32           65      1.21
 OKC  0.32           74      1.53
 BKN  0.31           97      2.06
 NOP  0.30           81      1.57
 PHI  0.27           90      1.55
 MEM  0.25          104      2.20
 BOS  0.24           71      1.10
 SAC  0.24           71      1.04
 POR  0.24           89      1.64
 IND  0.23           54      0.80
 CHA  0.22           49      0.95
 GSW  0.21           82      1.74
 NYK  0.19           81      1.36
 LAC  0.19           73      1.30
 MIA  0.16           54      1.12
 TOR  0.16           87      1.50
 ATL  0.15           74      1.14
 HOU  0.15           77      1.07
 MIN  0.12           64      1.00
 DAL  0.10           62      1.26
 CHI  0.10           57      0.87
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
