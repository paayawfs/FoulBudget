# Phase A feasibility audit — foul-trouble exposure (dev slice, 3 seasons)

players with ANY foul-trouble time: 617
total foul-trouble possessions (approx): 46,878

## per player-SEASON foul-trouble possessions (quantiles)
0.10     3.5
0.25     8.9
0.50    22.8
0.75    51.1
0.90    87.5

## per player POOLED across 3 seasons (quantiles)
0.10      5.4
0.25     14.0
0.50     46.3
0.75    105.2
0.90    187.7

## players above candidate thresholds (pooled possessions)
  >= 100: 157
  >= 250: 39
  >= 500: 4

## histogram, pooled possessions per player
```
      0-   25:  214 ########################################
     25-   50:  107 ####################
     50-  100:  139 ##########################
    100-  150:   68 #############
    150-  250:   50 #########
    250-  400:   30 ######
    400-  600:    7 #
    600-  684:    2 #
```

## state coverage: foul-trouble minutes by period
period
1    23.0
2    13.0
3    26.1
4    38.0
mean |margin| in trouble: 8.6 (vs 8.3 overall)

## pooled kappa-bar by foul-rate tier (pts/48, minutes-weighted WLS)
                         per48     t
foul_trouble[high-foul]   1.96  1.60
foul_trouble[low-foul]   10.09  5.47
foul_trouble[mid-foul]    3.08  2.12

## pooled kappa-bar by minutes tier (pts/48, minutes-weighted WLS)
                        per48     t
foul_trouble[high-min]   4.51  3.29
foul_trouble[low-min]    3.09  1.99
foul_trouble[mid-min]    4.19  2.93

## Decision (Phase A output, dev-slice edition)

1. **Sparsity confirms the plan's prerequisite.** Median player-season logs
   ~23 foul-trouble possessions; pooled across 3 seasons the median is 46.
   Only 4 players clear 500 pooled possessions, 39 clear 250. Per-player
   kappa_i on this slice would be prior, not measurement. With the planned
   ~20-season expansion, pooled counts scale roughly 7x (median ~300;
   hundreds of players above 250) and per-player deviations become viable
   for rotation regulars.
2. **Grouping variable: foul-rate tier.** Tier kappa-bars separate
   meaningfully (low-foul +10.1/48, t=5.5; mid +3.1; high-foul +2.0,
   t=1.6) while minutes tiers do not (3.1-4.5, overlapping). Caution: the
   low-foul tier's large kappa-bar carries the strongest selection (those
   players reach trouble rarely; coaches leave them in only when
   comfortable) -- treat as upper bound.
3. **Position grouping untested** -- positions are not in the play-by-play;
   requires a roster join before it can compete with foul-rate tier.
4. **Fallback posture:** if expansion slips, outcome-3 language
   (archetype-level kappa by foul-rate tier) is already supported by this
   slice; the gradient above IS the archetype result.

Rerun this audit after data expansion; thresholds and the grouping call
get re-decided then (per HIERARCHICAL_KAPPA_PLAN.md, the real decision
happens on expanded data).
