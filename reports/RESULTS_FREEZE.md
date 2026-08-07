# RESULTS_FREEZE.md — definitive numbers for the abstract and paper

Frozen 2026-07-24 at tag `results-freeze-v1`. Validation suite: 27 checks,
0 FAIL. Nothing below changes without unfreezing, and any unfreeze must be
logged here.

**v2 update 2026-07-26 (tag `results-freeze-v2-ot-fix`, supersedes v1 —
v1 content below is kept as-is for a direct diff):** fixed a bug in the
foul-trouble definition. The threshold was `foul_count >= period + 1`
everywhere (kappa estimation, B0, the DP's conventional policy, occurrence
selection). In overtime (period >= 5) this requires >= 6 fouls, which is
already disqualification — a player still on the floor could structurally
never be flagged in foul trouble during OT. Fixed via one shared function,
`config.foul_trouble_threshold(period) = min(period + 1, 5)` (regulation
unchanged; OT capped at 5, one foul from fouling out), imported everywhere
the threshold was previously duplicated. See REFERENCE.md SS3.4 for the
full rationale.

**Magnitude captured (measured before rerunning anything, across the full
2021-22..2025-26 window):** 666 newly-captured foul-trouble spells, 1,601
minutes, **3.92% of total foul-trouble exposure** (not a sub-1% footnote —
material enough to move kappa and B0). 283 player-games get a foul-trouble
occurrence that didn't exist under the old definition at all (their only
qualifying state was in OT). Restricted to 2025-26 (the evaluation season):
120 newly-captured spells, 64 brand-new player-game occurrences.

**What moved and what didn't, and why:**
- **kappa (pooled):** +4.22 -> **+3.98 per 48** (t: 6.7 -> 6.4). Real
  movement — kappa estimation is a plain WLS regression on real
  net-rating data with no DP involved, so it genuinely gains the
  newly-captured OT exposure.
- **Foul-rate hazard multiplier:** x0.641 -> **x0.647** (also a plain
  regression, small movement in the same direction: less negative
  adaptation once OT spells dilute the pooled estimate slightly).
- **B0 verdict: unchanged (SELECTION-DRIVEN).** FORCED DiD kappa-bar moved
  from -0.59/48 (t=-0.24, 5,859 poss) to **-1.96/48 (t=-0.93, 7,781 poss)**
  — more negative, on a meaningfully larger FORCED sample (OT spells feed
  FORCED exposure directly, since B0's clutch-window already treated all
  OT time as clutch). The fix did not flip the finding; if anything it
  strengthens it.
- **kappa_v2 (per-player) OOS gain:** +0.031% -> +0.029% of held-out MSE.
  Unchanged verdict (weak heterogeneity, pooled kappa-bar stands).
- **Headline wins/team/season at kappa = 0 (the causal claim): 0.65 ->
  0.65. Unchanged.** This is not a coincidence: confirmed directly in
  `src/policy/solver.py` that the DP's time lattice (`N_STEPS = 2880 // 30`)
  covers regulation only, and `period_of_step` clamps to period <= 4, so
  the backward induction never represents OT at all. Any exposure spell
  starting in OT gets `t_rem = 0` in `evaluate_convention_cost`, landing
  on the terminal boundary state where `V_opt` and `V_conv` are identical
  by construction — so every newly-captured OT occurrence contributes
  `cost_wp = 0` exactly, regardless of kappa. Verified empirically: the
  216-player E6 table's **season-total column** (`total_pp`) is
  byte-identical at kappa = 0 to the pre-fix numbers (Jokic 37.73pp,
  Wembanyama 31.90pp, Brooks 6.94pp/rank 99, all unchanged) even though
  occurrence counts rose — zero-cost additions to a sum leave the sum
  unchanged. The **per-occurrence mean** (`mean_pp`) is not byte-identical:
  it is the unchanged total divided by a larger occurrence count, so it
  shifts down slightly for every player who picked up OT occurrences. This is a separate,
  pre-existing structural limitation (the DP was never built to model
  overtime), not fixed here — out of scope for a threshold-only
  correction and flagged, not patched, per the project's frozen-scope
  rule. A future session would need an OT-aware time grid, an OT margin-
  step distribution, and OT hazard multipliers (currently `hazard_table`
  only has columns for periods 1-4) to close this gap.
- **Headline wins/team/season at estimated kappa (descriptive only): 2.05
  -> 1.95.** Tracks kappa's small decrease; per-occurrence WP cost 2.54pp
  -> 2.36pp. Occurrence count: 2,423 -> 2,485 (+62, mostly zero-cost as
  explained above).
- **E8 opponent-strength split: still PASS.** kappa=0 mean cost per
  occurrence by opponent-net-rating tercile: 0.76 / 0.79 / 0.78pp
  (strong/average/weak), still flat, same conclusion.
- **Team/player rankings at kappa = 0 (E6/E7): unchanged in substance.**
  Same top players (Jokic, Wembanyama, LaRavia), same team order (DET/UTA
  tied at 1.22, PHX 6th at 0.91, MIN the floor at 0.20) — the underlying
  kappa=0 numbers per existing occurrence didn't move, so rankings built
  on them don't either. `wins_est`/`mean_pp_est`/`total_pp_est` appendix
  columns shrank slightly across the board, tracking the smaller kappa.

**Bottom line for the abstract:** the causal claim (0.65 wins/team/season
at kappa = 0) is robust to this bug fix — it did not move. The descriptive
estimated-kappa numbers shifted modestly downward (2.05 -> 1.95 wins). The
B0 selection-driven verdict, already the paper's operative finding, is
if anything reinforced. No headline framing language needs to change.

**Update 2026-07-24 (post-tag, pre-abstract):** E6/E7 were regenerated with
kappa = 0 as the PRIMARY ranking column instead of estimated kappa, per the
B0 selection-driven verdict — the estimated-kappa ordering was quoting a
finding (the size and identity of the biggest kappa-financed stories) that
does not survive its own identification check. The "Player and team
slices" section below reflects the re-ranked tables. Core estimates and
the headline are unchanged; only which players/teams the paper points to
changed. 27 checks, 0 FAIL after the rerun.

**v3 update 2026-08-07 (tag `results-freeze-v3-pic`, supersedes v2 —
headline framing language DOES need to change this time):** respecified
the conventional policy πc. It previously forced PLAY whenever
`f < foul_trouble_threshold(period)`, regardless of whether playing was
actually optimal there. For below-replacement players (δ ≤ 0), π* sits at
every state regardless of foul trouble, so a large share of the old
headline was measuring "this player is below replacement," not the
foul-trouble convention — and that share was invariant to kappa, since
kappa only enters the drift term while `f >= threshold`. Confirmed
directly: at kappa = 0, wins(δ>0) = 0.283059, wins(δ≤0) = 0.000000 (56% of
the old 0.645 headline was this artifact). Fixed in `src/policy/solver.py`:
πc now plays optimally (argmax over play/sit) below threshold and is
forced to sit only at/above it, so π* and πc diverge only on the
convention itself — a one-line change (`ev_play_c if f < threshold else
ev_sit_c` → `ev_sit_c` if in trouble, else `max(ev_play_c, ev_sit_c)`).

**What moved:**
- **Headline wins/team/season at kappa = 0 (the causal claim): 0.65 ->
  0.28.** Entirely from delta>0 players; the delta<=0 component is exactly
  zero (a value-dominance argument guarantees V^πc <= V^π* pointwise, and
  they're equal wherever πc already matches π* — confirmed empirically, 0
  negative WP costs among 2,485 occurrences, C2 PASS).
- **Headline wins/team/season at estimated kappa (descriptive only): 1.95
  -> 1.59.** Per-occurrence WP cost: kappa=0 0.80pp -> 0.34pp; estimated
  kappa 2.36pp -> 1.92pp.
- **E8 opponent-strength split: still PASS.** kappa=0 mean cost per
  occurrence by opponent-net-rating tercile: 0.34 / 0.34 / 0.34pp
  (strong/average/weak) — flatter than before (was 0.76/0.79/0.78), still
  no opponent-strength dependence.
- **Team/player rankings at kappa = 0 (E6/E7): reshuffled.** Players and
  teams with delta<=0 (or near-zero delta) drop toward zero cost; the
  ranking is now effectively restricted to delta>0 players. See "Player
  and team slices" below for the new top/bottom.
- **Occurrence count, kappa (pooled), foul-rate hazard multiplier, B0
  FORCED/CHOSEN kappa-bar: all unchanged** (2,485 occurrences; kappa
  +3.98/48, t=6.41; hazard x0.647; B0 FORCED -1.96/48, t=-0.93 vs CHOSEN
  +4.19/48). These are plain regressions or occurrence-selection outputs,
  untouched by a change to the DP's conventional-policy branch.
- **kappa\* (re-solved under the new πc):** the kappa at which the
  headline cost reaches zero is approximately -0.17 to -0.18/min (-8.2 to
  -8.6 per 48), found by bisection on `evaluate_convention_cost`. The B0
  95% CI on the FORCED DiD estimate is (-6.10, +2.18) per 48 (from
  -1.96/48, t=-0.93 => SE ~2.11/48). kappa\* sits **outside** (more
  negative than) the CI's lower bound — even the most pessimistic
  plausible causal kappa within the CI leaves the kappa=0 headline
  positive (wins ~0.003 at the CI's lower edge), so the corrected floor is
  robust to the full extent of the estimation uncertainty on kappa.

**Bottom line for the abstract:** the causal claim moves from "at least
0.65 wins/team/season" to **"at least 0.28 wins/team/season."** This is
not a weaker result — it is the same finding measured without a
policy-specification artifact that inflated it by including a decision
(bench a below-replacement player) that has nothing to do with foul
trouble. The B0 selection-driven verdict is unchanged, and the corrected
floor is robust to the full B0 confidence interval on kappa. Headline
framing language DOES need updating (see "Headline" and "one-sentence
framing" sections below, already updated to 0.28).

## Headline (verdict-dependent framing, B0 = selection-driven)

**Conventional foul-trouble benching costs at least 0.28 wins per team per
season (0.34 percentage points of win probability per occurrence). This
floor is computed at kappa = 0, under a conventional policy that isolates
the benching convention itself (optimal everywhere else), and is the
paper's causal claim.**

The larger figure of 1.59 wins per team per season (1.92pp per occurrence)
uses the estimated kappa and, per the pre-registered B0 selection check,
is *descriptive accounting of the convention as currently managed*, never
a causal claim. The B0 verdict is final under its pre-registered stopping
rule: in FORCED exposure, where coaches have no real benching option
(final 7 minutes, margin within 6, take-foul window excluded, 7,781
possessions), the foul-trouble performance shift is negative, minus 1.96 per 48
(t = negative 0.93), against +4.19 per 48 in CHOSEN exposure. The pooled
kappa is coach selection, not player adaptation. The kappa=0 floor is also
robust to the B0 95% CI on kappa: re-solving for the kappa at which the
floor reaches zero gives kappa* ~ -8.2 to -8.6 per 48, outside (more
negative than) the CI's lower bound of -6.10 per 48. Abstract leads with
the floor. (tags `b0-final`, `results-freeze-v3-pic`)

## Core estimates

| quantity | value | tag |
|---|---|---|
| foul-trouble hazard multiplier (gamma_1, foul-rate adaptation) | x0.647 | `kappa-v2` |
| pooled kappa (performance shift in foul trouble, descriptive) | +3.98 per 48 (t = 6.4) | `kappa-v2` |
| B0 FORCED kappa (DiD, the identification test) | −1.96 per 48 (t = −0.93) | `b0-final` |
| kappa* (headline reaches zero, re-solved under πc v3) | ~-8.2 to -8.6 per 48 | `results-freeze-v3-pic` |
| foul-trouble occurrences evaluated (2025-26) | 2,485 | `results-freeze-v3-pic` |
| WP cost per occurrence, kappa = 0 / estimated kappa | 0.34pp / 1.92pp | `results-freeze-v3-pic` |
| wins per team per season, kappa = 0 / estimated kappa | 0.28 / 1.59 | `results-freeze-v3-pic` |

Note the two adaptation channels are distinct and only one survived B0:
the foul-RATE adaptation (players in trouble foul at 0.64x their base
hazard) is estimated on within-player variation and stands; the
performance kappa does not survive forced exposure and is descriptive.

## Player and team slices (E6/E7, tag `results-freeze-v3-pic`, RE-RANKED at kappa = 0, πc respecified)

Per the B0 selection-driven verdict, kappa = 0 is now the PRIMARY ranking
(unsuffixed mean_pp/total_pp/wins columns); estimated-kappa columns
(mean_pp_est/total_pp_est/wins_est) are a non-defensible as-managed
appendix only, never a ranking basis. The v3 πc respecification zeroes
out the delta<=0 tail (358 players evaluated, 216 with >=5 occurrences —
same eligibility counts as before; 182 of the 358 now sit at mean_pp <= 0,
exactly the delta<=0 set):
- Largest defensible season cost: N. Jokić, 37.7pp total at kappa = 0
  (19 occurrences; 61.7pp / 3.25pp-per-occurrence as-managed, appendix
  only) — unchanged from v2, since Jokić's delta is high enough that
  optimal already plays every trouble state under either πc definition.
- Largest defensible per-occurrence cost: G. Antetokounmpo, 2.60pp
  (6 occurrences; 4.40pp as-managed, appendix only). V. Wembanyama is 3rd
  at kappa = 0 (2.28pp, 14 occurrences) — still 2nd by season total (31.9pp).
  M. Smart is now the as-managed (mean_pp_est) per-occurrence leader
  (4.63pp, 9 occurrences), not Wembanyama.
- **Reversal:** D. Brooks topped the as-managed season-total table
  (106.2pp, kappa_share 0.93) but falls to 42nd of 358 players at kappa = 0
  — his defensible season total is 6.9pp. He was the single largest
  kappa-financed story in the pre-B0 tables and does not survive the
  selection-driven verdict.
- Cheapest occurrences (unchanged in kind): several bench players floor at
  ~0.00pp defensible cost even with a large as-managed appendix number
  (e.g. J. Wells ~0.00pp defensible vs 38.9pp as-managed, 12 occurrences)
  — at kappa = 0 the model finds no policy gap for these low-delta
  players, so 100% of their as-managed cost was the boost.
- **Team ordering reversal:** ORL now leads at kappa = 0 (0.585 wins, 107
  occurrences), not DET/UTA — DET drops to 3rd (0.530, 125 occurrences),
  UTA to 8th (0.351, 127 occurrences). PHX is still the as-managed
  (wins_est) leader (3.06 wins) but sits 4th at kappa = 0 (0.49). IND is
  still the as-managed floor (0.80 wins_est) but is not the kappa=0 floor
  (IND sits at 0.23); CHI is now the floor (0.10), with DAL (0.10) and
  MIN (0.12) close behind — MIN was the v2 floor (0.20) and is no longer.
  Ratio of highest to lowest team cost: 6.15x (ORL/CHI).

## Opponent-strength robustness (E8, tag `results-freeze-v3-pic`): PASS

Mean cost per occurrence at kappa = 0 by opponent team-season net-rating
tercile: strong 0.341pp, average 0.344pp, weak 0.340pp — essentially flat
(was 0.79/0.81/0.80pp under the pre-fix πc). The cost is flat in opponent
strength; the floor is not an artifact of blowout or weak-opponent states.
The secondary on-floor lineup RAPM split shows the same pattern.

## The one-sentence framing the abstract uses

Conventional foul-trouble benching costs NBA teams at least 0.28 wins per
team per season even under the most conservative assumption that players
perform no differently in foul trouble, and the widely feared
playing-scared effect does not appear where coaches are forced to test it.
