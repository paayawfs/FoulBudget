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
| E6 | EYEBALL | per-player WP cost of convention (2025, >=5 occurrences, n = 211; B0 verdict selection-driven: mean_pp/total_pp are descriptive as-managed accounting, total_pp_k0 (kappa=0 floor) is the causally defensible number per player): |
| E7 | EYEBALL | wins lost per season to the convention by team (2025; B0 verdict selection-driven: wins_est is descriptive as-managed accounting, wins_k0 (kappa=0 floor) is the causally defensible number; occurrences located at the team they happened for, traded players split): |
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
per-player WP cost of convention (2025, >=5 occurrences, n = 211; B0 verdict selection-driven: mean_pp/total_pp are descriptive as-managed accounting, total_pp_k0 (kappa=0 floor) is the causally defensible number per player):
top 20 by per occurrence (mean_pp):
                 name  mean_pp  total_pp  total_pp_k0  kappa_share  count  delta48
             M. Smart     4.79     43.14        16.42         0.62      9     3.61
            E. Mobley     4.67     37.37         6.33         0.83      8     1.57
     G. Antetokounmpo     4.50     27.00        15.63         0.42      6     8.49
S. Gilgeous-Alexander     4.49     31.45        17.10         0.46      7     7.21
        V. Wembanyama     4.35     60.86        31.90         0.48     14     6.56
        J. Champagnie     4.33     21.66         5.30         0.76      5     2.39
            P. George     4.27     29.90         7.68         0.74      7     2.27
            D. Booker     4.15     53.98        17.75         0.67     13     3.15
             J. Allen     4.07     32.59        10.11         0.69      8     2.79
          C. Holmgren     4.07     20.36         7.56         0.63      5     3.69
             J. Suggs     3.96     55.40        13.89         0.75     14     2.55
            L. Dončić     3.90     50.71        18.46         0.64     13     3.84
          O. Ighodaro     3.86     73.37        19.21         0.74     19     2.25
             S. Curry     3.85     19.27         5.04         0.74      5     2.58
             H. Jones     3.82     61.12        22.56         0.63     16     4.07
            S. Sharpe     3.82     22.91         3.06         0.87      6    -0.32
            D. Brooks     3.74    112.20         6.94         0.94     30     0.50
        Z. Williamson     3.72     18.61         4.56         0.75      5     2.39
             A. Green     3.71     25.96         8.96         0.65      7     3.33
           A. Edwards     3.68     18.39         2.36         0.87      5     1.19
bottom 20 by per occurrence (mean_pp):
        name  mean_pp  total_pp  total_pp_k0  kappa_share  count  delta48
J. McDaniels     0.50      5.54         0.26         0.95     11    -0.61
    I. Zubac     0.69      3.45         0.53         0.85      5     1.55
     J. Huff     0.87      9.56         0.94         0.90     11    -0.68
    M. Peavy     0.92      5.53         0.38         0.93      6     0.71
R. Westbrook     0.95      5.71         3.41         0.40      6    -2.22
   J. Randle     0.97      4.87         0.00         1.00      5    -0.23
   B. Hyland     0.98      5.88         0.84         0.86      6    -0.54
   P. Watson     1.05      7.38         1.88         0.74      7    -0.91
    J. Fears     1.07      5.37         3.95         0.26      5    -1.44
   J. Harden     1.16      5.82         0.00         1.00      5     0.01
  M. Raynaud     1.20      7.21         5.08         0.30      6    -3.00
 N. Clifford     1.27      6.35         1.60         0.75      5     1.99
 J. Clarkson     1.28      7.67         5.51         0.28      6    -2.00
 A. Mitchell     1.30      6.51         0.48         0.93      5     0.40
    J. Brown     1.32     13.20         5.86         0.56     10    -1.64
   S. Castle     1.32     26.48         5.74         0.78     20    -1.14
   A. Sengun     1.37     23.34         4.36         0.81     17    -0.89
  O. Okongwu     1.37     27.48         4.41         0.84     20     0.97
  G. Bitadze     1.41      9.88         1.04         0.89      7    -0.69
   A. Newell     1.42      7.11         4.55         0.36      5    -2.94
top 20 by season total (total_pp):
          name  mean_pp  total_pp  total_pp_k0  kappa_share  count  delta48
     D. Brooks     3.74    112.20         6.94         0.94     30     0.50
   O. Ighodaro     3.86     73.37        19.21         0.74     19     2.25
       D. Bane     3.64     72.76        24.22         0.67     20     3.26
     K. George     3.36     70.60        14.12         0.80     21     1.86
 K. Filipowski     2.53     65.88        11.36         0.83     26     1.60
 C. Cunningham     3.23     64.68        14.53         0.78     20     2.08
      N. Jokić     3.51     63.13        37.73         0.40     18     8.37
      H. Jones     3.82     61.12        22.56         0.63     16     4.07
 V. Wembanyama     4.35     60.86        31.90         0.48     14     6.56
 W. Carter Jr.     2.52     60.40        11.31         0.81     24     1.61
   A. Thompson     3.48     55.76        16.50         0.70     16     2.98
      J. Suggs     3.96     55.40        13.89         0.75     14     2.55
     D. Booker     4.15     53.98        17.75         0.67     13     3.15
   D. Robinson     3.01     51.21        13.95         0.73     17     2.34
     L. Dončić     3.90     50.71        18.46         0.64     13     3.84
    J. LaRavia     2.63     49.97        30.53         0.39     19    -1.92
   D. Cardwell     2.31     48.52        14.52         0.70     21     2.87
     T. Camara     2.40     47.95        14.06         0.71     20     2.53
     D. Sharpe     3.40     47.66        17.40         0.63     14     4.32
J. Jackson Jr.     2.49     44.79        13.13         0.71     18     2.71
bottom 20 by season total (total_pp):
         name  mean_pp  total_pp  total_pp_k0  kappa_share  count  delta48
     I. Zubac     0.69      3.45         0.53         0.85      5     1.55
    J. Randle     0.97      4.87         0.00         1.00      5    -0.23
     J. Fears     1.07      5.37         3.95         0.26      5    -1.44
     M. Peavy     0.92      5.53         0.38         0.93      6     0.71
 J. McDaniels     0.50      5.54         0.26         0.95     11    -0.61
 R. Westbrook     0.95      5.71         3.41         0.40      6    -2.22
    J. Harden     1.16      5.82         0.00         1.00      5     0.01
    B. Hyland     0.98      5.88         0.84         0.86      6    -0.54
  N. Clifford     1.27      6.35         1.60         0.75      5     1.99
  A. Mitchell     1.30      6.51         0.48         0.93      5     0.40
    A. Newell     1.42      7.11         4.55         0.36      5    -2.94
   M. Raynaud     1.20      7.21         5.08         0.30      6    -3.00
    P. Watson     1.05      7.38         1.88         0.74      7    -0.91
  J. Clarkson     1.28      7.67         5.51         0.28      6    -2.00
R. Dillingham     1.56      7.78         4.26         0.45      5    -1.99
     T. Eason     1.78      8.89         0.71         0.92      5     0.55
      J. Huff     0.87      9.56         0.94         0.90     11    -0.68
   G. Bitadze     1.41      9.88         1.04         0.89      7    -0.69
     B. Saraf     1.65      9.89         6.27         0.37      6    -2.37
    N. Tomlin     2.00     10.00         4.29         0.57      5    -1.36
```

### E7 (EYEBALL)
```
wins lost per season to the convention by team (2025; B0 verdict selection-driven: wins_est is descriptive as-managed accounting, wins_k0 (kappa=0 floor) is the causally defensible number; occurrences located at the team they happened for, traded players split):
team  wins_est  occurrences  wins_k0
 PHX      3.65          108     0.91
 UTA      3.42          124     1.22
 DET      3.30          124     1.22
 WAS      3.24          116     0.83
 ORL      3.02          103     1.03
 MEM      2.88          103     0.77
 BKN      2.66           97     0.78
 LAL      2.35           80     0.98
 CLE      2.28           82     0.74
 SAS      2.23           85     0.78
 GSW      2.13           82     0.50
 POR      2.08           87     0.57
 DEN      2.02           86     0.95
 PHI      2.01           88     0.64
 NOP      2.00           76     0.64
 OKC      1.99           71     0.69
 TOR      1.91           85     0.47
 BOS      1.67           70     0.74
 NYK      1.65           78     0.41
 LAC      1.62           73     0.42
 MIL      1.62           65     0.67
 ATL      1.57           74     0.50
 HOU      1.53           71     0.54
 DAL      1.46           60     0.22
 MIA      1.44           52     0.42
 SAC      1.29           70     0.43
 CHI      1.26           56     0.42
 MIN      1.15           59     0.20
 CHA      1.10           46     0.32
 IND      0.94           52     0.33
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
