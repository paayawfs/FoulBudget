# RESULTS_FREEZE.md — definitive numbers for the abstract and paper

Frozen 2026-07-24 at tag `results-freeze-v1`. Validation suite: 27 checks,
0 FAIL. Nothing below changes without unfreezing, and any unfreeze must be
logged here.

**Update 2026-07-24 (post-tag, pre-abstract):** E6/E7 were regenerated with
kappa = 0 as the PRIMARY ranking column instead of estimated kappa, per the
B0 selection-driven verdict — the estimated-kappa ordering was quoting a
finding (the size and identity of the biggest kappa-financed stories) that
does not survive its own identification check. The "Player and team
slices" section below reflects the re-ranked tables. Core estimates and
the headline are unchanged; only which players/teams the paper points to
changed. 27 checks, 0 FAIL after the rerun.

## Headline (verdict-dependent framing, B0 = selection-driven)

**Conventional foul-trouble benching costs at least 0.65 wins per team per
season (0.80 percentage points of win probability per occurrence). This
floor is computed at kappa = 0 and is the paper's causal claim.**

The larger figure of 2.05 wins per team per season (2.54pp per occurrence)
uses the estimated kappa and, per the pre-registered B0 selection check,
is *descriptive accounting of the convention as currently managed*, never
a causal claim. The B0 verdict is final under its pre-registered stopping
rule: in FORCED exposure, where coaches have no real benching option
(final 7 minutes, margin within 6, take-foul window excluded, 5,859
possessions), the foul-trouble performance shift is negative, minus 0.59 per 48
(t = negative 0.24), against +4.25 per 48 in CHOSEN exposure. The pooled
kappa is coach selection, not player adaptation. Abstract leads with the
floor. (tag `b0-final`)

## Core estimates

| quantity | value | tag |
|---|---|---|
| foul-trouble hazard multiplier (gamma_1, foul-rate adaptation) | x0.641 | `kappa-v2` |
| pooled kappa (performance shift in foul trouble, descriptive) | +4.22 per 48 (t = 6.7) | `kappa-v2` |
| B0 FORCED kappa (DiD, the identification test) | −0.59 per 48 (t = −0.24) | `b0-final` |
| foul-trouble occurrences evaluated (2025-26) | 2,423 | `cost-tables-v1` |
| WP cost per occurrence, kappa = 0 / estimated kappa | 0.80pp / 2.54pp | `cost-tables-v1` |
| wins per team per season, kappa = 0 / estimated kappa | 0.65 / 2.05 | `cost-tables-v1` |

Note the two adaptation channels are distinct and only one survived B0:
the foul-RATE adaptation (players in trouble foul at 0.64x their base
hazard) is estimated on within-player variation and stands; the
performance kappa does not survive forced exposure and is descriptive.

## Player and team slices (E6/E7, tag `cost-tables-v1`, RE-RANKED at kappa = 0)

Per the B0 selection-driven verdict, kappa = 0 is now the PRIMARY ranking
(unsuffixed mean_pp/total_pp/wins columns); estimated-kappa columns
(mean_pp_est/total_pp_est/wins_est) are a non-defensible as-managed
appendix only, never a ranking basis. Re-running E6/E7 at kappa = 0
reshuffles several stories from the pre-B0 as-managed ordering:
- Largest defensible season cost: N. Jokić, 37.7pp total at kappa = 0
  (18 occurrences; 63.1pp / 3.51pp-per-occurrence as-managed, appendix
  only).
- Largest defensible per-occurrence cost: G. Antetokounmpo, 2.60pp
  (6 occurrences; 4.50pp as-managed, appendix only). V. Wembanyama, the
  as-managed per-occurrence leader (4.35pp), drops to 6th at kappa = 0
  (2.28pp) — still 2nd by season total (31.9pp, 14 occurrences).
- **Reversal:** D. Brooks topped the as-managed season-total table
  (112.2pp, kappa_share 0.94) but falls to 99th of 358 players at kappa = 0
  — his defensible season total is 6.9pp. He was the single largest
  kappa-financed story in the pre-B0 tables and does not survive the
  selection-driven verdict.
- Cheapest occurrences (unchanged in kind): several bench players floor at
  0.00pp defensible cost even with a large as-managed appendix number
  (e.g. J. Wells 0.00pp defensible vs 41.2pp as-managed) — at kappa = 0 the
  model finds no policy gap for these low-delta players, so 100% of their
  as-managed cost was the boost.
- **Team ordering reversal:** DET and UTA tie for the most wins lost at
  kappa = 0 (1.22 each, 124 occurrences apiece), not PHX. PHX was the
  as-managed leader (3.65 wins) but drops to 6th at kappa = 0 (0.91).
  MIN loses the fewest at kappa = 0 (0.20, appendix 1.15); IND was the
  as-managed floor (0.94 appendix) but is not the kappa=0 floor
  (IND sits at 0.33; MIN is now the floor).

## Opponent-strength robustness (E8, tag `e8-opponent-split`): PASS

Mean cost per occurrence at kappa = 0 by opponent team-season net-rating
tercile: strong 0.79pp, average 0.81pp, weak 0.80pp. The cost is flat in
opponent strength; the floor is not an artifact of blowout or weak-opponent
states. The secondary on-floor lineup RAPM split shows the same pattern.

## The one-sentence framing the abstract uses

Conventional foul-trouble benching costs NBA teams at least 0.65 wins per
team per season even under the most conservative assumption that players
perform no differently in foul trouble, and the widely feared
playing-scared effect does not appear where coaches are forced to test it.
