# Phase A feasibility audit — foul-trouble exposure (5 analysis seasons: 2021–2025)

players with ANY foul-trouble time: 795
total foul-trouble possessions (approx): 81,815

## per player-SEASON foul-trouble possessions (quantiles)
0.10     3.5
0.25     9.2
0.50    23.9
0.75    50.6
0.90    89.0

## per player POOLED across 5 seasons (quantiles)
0.10      5.3
0.25     16.5
0.50     51.7
0.75    139.8
0.90    257.4

## players above candidate thresholds (pooled possessions)
  >= 100: 276
  >= 250: 83
  >= 500: 16

## histogram, pooled possessions per player
```
      0-   25:  257 ########################################
     25-   50:  124 ###################
     50-  100:  138 #####################
    100-  150:   89 ##############
    150-  250:  104 ################
    250-  400:   56 #########
    400-  600:   15 ##
    600- 1000:   11 ##
   1000- 1058:    1 #
```

## state coverage: foul-trouble minutes by period
period
1    22.6
2    13.5
3    26.9
4    37.1
mean |margin| in trouble: 8.8 (vs 8.4 overall)

## pooled kappa-bar by foul-rate tier (pts/48, minutes-weighted WLS)
                         per48     t
foul_trouble[high-foul]   3.16  3.47
foul_trouble[low-foul]    5.68  4.13
foul_trouble[mid-foul]    4.87  4.27

## pooled kappa-bar by minutes tier (pts/48, minutes-weighted WLS)
                        per48     t
foul_trouble[high-min]   4.16  3.98
foul_trouble[low-min]    4.66  4.07
foul_trouble[mid-min]    3.88  3.51

## Decision (Phase A output, 5-season window — the real one)

1. **Grouping variable: league-wide (single group).** The 3-season
   foul-rate-tier gradient did not replicate: on 5 seasons the tiers read
   +3.2 / +4.9 / +5.7 per 48 and the largest pairwise gap (low vs high
   foul) is 2.5 +/- 1.7 (t = 1.5). Minutes tiers are flat (gap 0.5,
   t = 0.3). Per the plan's rule — coarsest grouping whose groups still
   differ meaningfully — no grouping clears the bar, so the Phase B
   hierarchy is global kappa-bar + ridge-penalized per-player deviations,
   no intermediate group layer. The dev-slice low-foul +10.1 was noise
   and/or selection, exactly why the decision waited for expanded data.
2. **Sparsity is better but still thin.** Median pooled exposure is 52
   possessions (was 46 on 3 seasons); 276 players clear 100, 83 clear
   250, 16 clear 500. Per-player kappa_i remains a partial-pooling
   exercise, not free estimation.
3. **Reporting threshold: >= 250 pooled possessions** (83 players).
   Everyone below reports the global estimate (plan Phase C.2). If the
   Phase D out-of-sample gate shows ~0 gain, outcome-2 language applies
   ("data supports a pooled effect with limited individual variation").
4. **Position grouping still untested** (needs roster join). Only worth
   doing if reviewers ask: with foul-rate tiers this flat, position
   tiers clearing the bar is unlikely.
