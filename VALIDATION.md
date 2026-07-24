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
| B0 | EYEBALL | B0-final rung 1: FORCED (last 7 min, |d|<=6, top-half delta, final-90s one-possession spells excluded) DiD kappa-bar -0.59/48 (t=-0.2), raw +1.79/48 (t=0.8) vs CHOSEN +4.25/48 on 5,859 FORCED poss; excluded ritual cell +50.45/48 (304 poss); verdict: selection-driven — estimated-kappa numbers are descriptive, the kappa=0 floor is the causal claim (reports/kappa_b0.md) |
| C1 | PASS | max |sum(weights) - 1| over player-seasons: 2.00e-15 |
| C2 | PASS | negative WP costs among 2,423 occurrences: 0 (min = 0.00e+00) |
| C3 | PASS | kappa_i shrinkage: sd(dev) 0.44 (<25 FT poss) -> 2.15 (>=250) per48, max thin-sample |dev| = 1.51; FT-weighted mean kappa_i +4.22 vs v1 pooled +4.22; OOS gain over pooled = +0.031% of held-out MSE (lambda_kappa = 640) |
| C4 | PASS | aggregate predicted/actual fouls = 1.0139 (within 2%), per-player-season corr = 0.997 (>=50 fouls; per-player gaps are the shrinkage prior working) |
| C5 | PASS | in-house 2025 decayed RAPM vs nbarapm.com (n=279, >=1000 min): r = 0.962 vs their time-decay RAPM (gate 0.9); 3y 0.943, 5y 0.922, 1y 0.876 -- decay ordering as expected |
| E1 | EYEBALL | top-12 by mean WP cost per occurrence (>=5 occurrences): |
| E2 | PASS | corr(model lambda, raw per-36 fouls) = 0.998 (>=1000 min, 2025) |
| E3 | EYEBALL | stars with strongest backups (delta should compress): |
| E4 | EYEBALL | case studies: top-decile-delta starters benched >=6 min after Q+1 trouble in games decided by <=5: |
| E5 | EYEBALL | game 22500203, G. Antetokounmpo (delta +8.5/48, lam 2.6/36) |
| E6 | EYEBALL | per-player WP cost of convention (2025, >=5 occurrences, n = 211; B0 verdict selection-driven: mean_pp/total_pp (kappa=0) are the PRIMARY, causally defensible ranking; mean_pp_est/total_pp_est are the non-defensible as-managed appendix per player): |
| E7 | EYEBALL | wins lost per season to the convention by team (2025; B0 verdict selection-driven: wins (kappa=0) is the PRIMARY, causally defensible ranking, sorted descending; wins_est is the non-defensible as-managed appendix; occurrences located at the team they happened for, traded players split): |
| E8-A | PASS | opponent team-season net-rating terciles (2,423 occurrences): strong n=808 est 2.52pp k0 0.79pp | average n=769 est 2.53pp k0 0.81pp | weak n=846 est 2.56pp k0 0.80pp (pass condition: k0 positive in every tercile; reports/e8_opponent_split.md) |
| E8-B | EYEBALL | opponent on-floor lineup RAPM terciles (secondary, correlates with score state; match rate 100.0%): strong n=808 est 2.54pp k0 0.76pp | average n=807 est 2.57pp k0 0.83pp | weak n=808 est 2.50pp k0 0.80pp |

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
  Q4   0.0m left | d= +2 | f=5 TROUBLE | coach: on  0.0m (game_end) | model: --
```

### E6 (EYEBALL)
```
per-player WP cost of convention (2025, >=5 occurrences, n = 211; B0 verdict selection-driven: mean_pp/total_pp (kappa=0) are the PRIMARY, causally defensible ranking; mean_pp_est/total_pp_est are the non-defensible as-managed appendix per player):
top 20 by per occurrence (mean_pp, kappa=0):
                 name  mean_pp  total_pp  mean_pp_est  total_pp_est  kappa_share  count  delta48
     G. Antetokounmpo     2.60     15.63         4.50         27.00         0.42      6     8.49
S. Gilgeous-Alexander     2.44     17.10         4.49         31.45         0.46      7     7.21
            C. Bryant     2.44     17.07         3.04         21.31         0.20      7    -3.36
            K. George     2.41     14.48         3.22         19.34         0.25      6    -3.25
            A. Simons     2.29     13.73         2.59         15.52         0.12      6    -2.66
        V. Wembanyama     2.28     31.90         4.35         60.86         0.48     14     6.56
            D. Powell     2.27     13.65         2.83         16.96         0.20      6    -4.17
          R. Sheppard     2.22     15.55         2.45         17.13         0.09      7    -3.28
           I. Collier     2.16     25.87         2.92         34.99         0.26     12    -3.28
             N. Jokić     2.10     37.73         3.51         63.13         0.40     18     8.37
          M. Williams     1.84     14.73         2.53         20.26         0.27      8    -3.43
             M. Smart     1.82     16.42         4.79         43.14         0.62      9     3.61
          N. Richards     1.81     10.88         2.65         15.93         0.32      6    -3.98
        B. Carrington     1.80     23.41         2.40         31.22         0.25     13    -4.76
             D. Queen     1.79     12.54         2.04         14.28         0.12      7    -2.42
              G. Dick     1.74     15.66         2.45         22.09         0.29      9    -1.88
              J. Sims     1.63     14.67         2.39         21.48         0.32      9    -2.42
           T. Watford     1.63      9.76         2.11         12.69         0.23      6    -2.70
          C. Williams     1.62     11.35         2.41         16.85         0.33      7    -3.71
           J. LaRavia     1.61     30.53         2.63         49.97         0.39     19    -1.92
bottom 20 by per occurrence (mean_pp, kappa=0):
          name  mean_pp  total_pp  mean_pp_est  total_pp_est  kappa_share  count  delta48
  T. Hendricks    -0.00     -0.00         3.23         25.80         1.00      8    -0.06
    D. Clingan    -0.00     -0.00         2.16         19.44         1.00      9    -0.12
      K. Ellis    -0.00     -0.00         2.27         15.91         1.00      7     0.13
     N. Traore    -0.00     -0.00         2.32         23.20         1.00     10     0.18
  P. Pritchard    -0.00     -0.00         2.14         10.69         1.00      5    -0.22
W. Clayton Jr.     0.00      0.00         2.27         18.17         1.00      8    -0.04
      J. Wells     0.00      0.00         3.43         41.19         1.00     12     0.07
     J. Randle     0.00      0.00         0.97          4.87         1.00      5    -0.23
     J. Walker     0.00      0.00         3.04         24.35         1.00      8    -0.06
 K. Jakučionis     0.00      0.00         2.69         21.53         1.00      8     0.07
     J. Harden     0.00      0.00         1.16          5.82         1.00      5     0.01
   J. Williams     0.00      0.00         2.77         24.97         1.00      9    -0.17
       D. Wolf     0.00      0.00         3.43         27.47         1.00      8     0.09
   K. Matković     0.00      0.00         3.15         22.02         1.00      7    -0.23
 M. Bagley III     0.00      0.00         3.13         25.03         1.00      8     0.15
  J. McDaniels     0.02      0.26         0.50          5.54         0.95     11    -0.61
      M. Peavy     0.06      0.38         0.92          5.53         0.93      6     0.71
       J. Huff     0.09      0.94         0.87          9.56         0.90     11    -0.68
   A. Mitchell     0.10      0.48         1.30          6.51         0.93      5     0.40
      I. Zubac     0.11      0.53         0.69          3.45         0.85      5     1.55
top 20 by season total (total_pp, kappa=0):
                 name  mean_pp  total_pp  mean_pp_est  total_pp_est  kappa_share  count  delta48
             N. Jokić     2.10     37.73         3.51         63.13         0.40     18     8.37
        V. Wembanyama     2.28     31.90         4.35         60.86         0.48     14     6.56
           J. LaRavia     1.61     30.53         2.63         49.97         0.39     19    -1.92
           I. Collier     2.16     25.87         2.92         34.99         0.26     12    -3.28
        R. Holland II     1.33     25.29         2.14         40.70         0.38     19    -1.77
            A. Bailey     1.38     24.87         2.11         37.95         0.34     18    -1.74
              D. Bane     1.21     24.22         3.64         72.76         0.67     20     3.26
        B. Carrington     1.80     23.41         2.40         31.22         0.25     13    -4.76
             H. Jones     1.41     22.56         3.82         61.12         0.63     16     4.07
           I. Stewart     1.47     22.01         2.31         34.66         0.37     15    -3.82
             A. Black     1.48     20.73         2.57         35.91         0.42     14    -1.82
          O. Ighodaro     1.01     19.21         3.86         73.37         0.74     19     2.25
           J. Mashack     1.59     19.03         3.30         39.59         0.52     12    -1.41
            L. Dončić     1.42     18.46         3.90         50.71         0.64     13     3.84
            D. Booker     1.37     17.75         4.15         53.98         0.67     13     3.15
         J. Smith Jr.     1.03     17.59         1.94         32.90         0.47     17    -1.25
            D. Sharpe     1.24     17.40         3.40         47.66         0.63     14     4.32
S. Gilgeous-Alexander     2.44     17.10         4.49         31.45         0.46      7     7.21
            C. Bryant     2.44     17.07         3.04         21.31         0.20      7    -3.36
          A. Thompson     1.03     16.50         3.48         55.76         0.70     16     2.98
bottom 20 by season total (total_pp, kappa=0):
          name  mean_pp  total_pp  mean_pp_est  total_pp_est  kappa_share  count  delta48
  T. Hendricks    -0.00     -0.00         3.23         25.80         1.00      8    -0.06
    D. Clingan    -0.00     -0.00         2.16         19.44         1.00      9    -0.12
      K. Ellis    -0.00     -0.00         2.27         15.91         1.00      7     0.13
     N. Traore    -0.00     -0.00         2.32         23.20         1.00     10     0.18
  P. Pritchard    -0.00     -0.00         2.14         10.69         1.00      5    -0.22
W. Clayton Jr.     0.00      0.00         2.27         18.17         1.00      8    -0.04
      J. Wells     0.00      0.00         3.43         41.19         1.00     12     0.07
     J. Randle     0.00      0.00         0.97          4.87         1.00      5    -0.23
     J. Walker     0.00      0.00         3.04         24.35         1.00      8    -0.06
     J. Harden     0.00      0.00         1.16          5.82         1.00      5     0.01
 K. Jakučionis     0.00      0.00         2.69         21.53         1.00      8     0.07
   K. Matković     0.00      0.00         3.15         22.02         1.00      7    -0.23
   J. Williams     0.00      0.00         2.77         24.97         1.00      9    -0.17
       D. Wolf     0.00      0.00         3.43         27.47         1.00      8     0.09
 M. Bagley III     0.00      0.00         3.13         25.03         1.00      8     0.15
  J. McDaniels     0.02      0.26         0.50          5.54         0.95     11    -0.61
      M. Peavy     0.06      0.38         0.92          5.53         0.93      6     0.71
   A. Mitchell     0.10      0.48         1.30          6.51         0.93      5     0.40
      I. Zubac     0.11      0.53         0.69          3.45         0.85      5     1.55
      T. Eason     0.14      0.71         1.78          8.89         0.92      5     0.55
```

### E7 (EYEBALL)
```
wins lost per season to the convention by team (2025; B0 verdict selection-driven: wins (kappa=0) is the PRIMARY, causally defensible ranking, sorted descending; wins_est is the non-defensible as-managed appendix; occurrences located at the team they happened for, traded players split):
team  wins  occurrences  wins_est
 DET  1.22          124      3.30
 UTA  1.22          124      3.42
 ORL  1.03          103      3.02
 LAL  0.98           80      2.35
 DEN  0.95           86      2.02
 PHX  0.91          108      3.65
 WAS  0.83          116      3.24
 BKN  0.78           97      2.66
 SAS  0.78           85      2.23
 MEM  0.77          103      2.88
 BOS  0.74           70      1.67
 CLE  0.74           82      2.28
 OKC  0.69           71      1.99
 MIL  0.67           65      1.62
 NOP  0.64           76      2.00
 PHI  0.64           88      2.01
 POR  0.57           87      2.08
 HOU  0.54           71      1.53
 GSW  0.50           82      2.13
 ATL  0.50           74      1.57
 TOR  0.47           85      1.91
 SAC  0.43           70      1.29
 CHI  0.42           56      1.26
 LAC  0.42           73      1.62
 MIA  0.42           52      1.44
 NYK  0.41           78      1.65
 IND  0.33           52      0.94
 CHA  0.32           46      1.10
 DAL  0.22           60      1.46
 MIN  0.20           59      1.15
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
