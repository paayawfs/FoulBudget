# HIERARCHICAL_KAPPA_PLAN.md — Per-player playing-scared estimation
## Upgrades pooled κ (v1) to player-specific κ_i with partial pooling.
## Prerequisite: data expansion (PROJECT_PLAN Phase 1). Foul-trouble stints
## are the binding constraint; do not attempt this on 3 seasons alone.

**Notation (pin this):** κ_i is the foul-trouble performance *deviation* for
player i, in RAPM units (points/100). κ_i = 0 means no playing-scared
effect. Negative = plays worse in foul trouble. The pooled v1 estimate is
κ̄. Update REFERENCE.md so every doc uses this convention.

---

## Phase A — Feasibility audit (do this BEFORE any modeling, ~1 session)

The entire design depends on one distribution: **foul-trouble possessions
per player per season.**

1. From the reconciled stint data, tabulate for every player-season:
   possessions on floor at fouls ≥ Q+1, split by season, plus opponent/
   score-state coverage.
2. Produce: histogram, quantile table (p10/25/50/75/90), and the count of
   players above candidate thresholds (≥100, ≥250, ≥500 foul-trouble
   possessions pooled across seasons).
3. **Decision output:** the grouping variable for pooling. Candidates:
   league-wide (single group), position, foul-rate tier, minutes tier.
   Choose the coarsest grouping whose groups still differ meaningfully in
   pooled κ̄ — finer grouping with these sample sizes is decoration.

Expect the truth to be ugly: median rotation player probably logs only
tens of foul-trouble possessions per season. That's fine — it's exactly
what partial pooling is for — but the audit tells you how much
individuality the data can actually support, and it feeds the honest-
claims decision in Phase E.

---

## Phase B0 — Selection check (identification defense for κ̄)

The pooled κ̄ > 0 is measured on coach-selected exposure: coaches choose who
plays through foul trouble. B0 asks how much of κ̄ survives where the coach
has no real choice. This blocks the paper's central claim — run it before
the abstract locks the headline.

**Design** (src/hazard/kappa_b0_selection.py → reports/kappa_b0.md +
summary row in VALIDATION.md):

1. Split all foul-trouble possessions in the behavioral window into:
   - **FORCED**: final 5.0 minutes of regulation (or any OT) with score
     margin within one possession (|d| ≤ 3), player's delta48 in the top
     half of rotation players (≥ 500 min) that season. Benching is not a
     live option there; these minutes are minimally coach-selected. (Under
     Q+1, OT contributes no foul-trouble exposure — trouble in period p
     requires p+1 ≥ 6 fouls — so FORCED foul-trouble mass is late-Q4
     five-foul spells.)
   - **CHOSEN**: every other foul-trouble possession.
   Cutoffs are named constants. If FORCED holds fewer than ~2,000
   foul-trouble possessions, widen margin to |d| ≤ 6, then the window to
   the final 7 minutes, logging each widening. Report subsample sizes
   prominently.
2. Estimate pooled κ̄ separately on FORCED and CHOSEN with the same spell
   WLS as v1/v2 (global columns only, no per-player deviations): point
   estimates, SEs, difference with t-stat. Tier-level split (foul-rate
   low/mid/high) on each subsample if cell sizes permit.
3. **Known confound, note either way:** FORCED minutes are high-leverage
   end-game minutes; intensity/effort differs from average minutes
   independent of foul trouble. Mitigation: also estimate the same
   FORCED-window performance shift for NON-foul-trouble players and
   difference it out (regression adds the window main effect; the
   foul-trouble × window coefficient then reads as the within-clutch
   foul-trouble shift). That DiD estimate is the cleaner number.
4. **Decision rule (no thumb on the scale):**
   - FORCED κ̄ remains significantly positive → adaptation is real; the
     estimated-kappa headline (2.05 wins) stands with B0 as its
     identification defense.
   - FORCED κ̄ ~0 or negative → the positive pooled κ̄ is substantially
     selection; the defensible headline shifts toward the κ = 0 floor
     (0.65 wins), paper language changes, and every downstream artifact
     it touches (headline table, per-player cost tables, top-20 lists)
     gets flagged.

---

## Phase B — Model specification (recommended: extend the RAPM regression)

**Core idea: κ estimation is one design-matrix extension away from
infrastructure you already have.** The RAPM ridge regression has a column
per player ("on floor"). Add, for each player, a second column:
"on floor AND at fouls ≥ Q+1." The coefficient on that interaction column
IS κ_i — the within-player performance shift under foul trouble, already
adjusted for teammates and opponents by the same regression that adjusts
everything else.

Shrinkage structure:
- Parameterize the interaction as **deviation from the pooled effect**:
  include one global foul-trouble column (coefficient κ̄, lightly
  penalized) plus per-player deviation columns (coefficient κ_i − κ̄,
  ridge-penalized toward 0). Ridge toward zero-deviation = partial pooling
  toward the group mean, using machinery you already trust.
- If Phase A picks a grouping finer than league-wide, add group-level
  foul-trouble columns between the global and per-player layers
  (global → group deviation → player deviation).
- Penalty for the deviation layer (λ_κ) chosen by cross-validation on
  held-out stints — do NOT reuse the RAPM penalty; the interaction
  columns are far sparser and need heavier regularization.

**Alternative if the ridge route misbehaves:** two-stage empirical Bayes —
estimate raw per-player κ̂_i with standard errors from unpenalized
interactions, then precision-weighted shrinkage toward the group mean
(κ_i = w_i·κ̂_i + (1−w_i)·κ̄_g, w_i = τ²/(τ² + se_i²), τ² by method of
moments). Cruder but transparent, and it produces the same C3 shrinkage
plot. Full Bayes (PyMC) is the third option; at RAPM design-matrix scale
it's slow and buys little over ridge — only go there if reviewers demand
posterior intervals.

Controls to add regardless of route:
- **Leverage/state controls:** foul-trouble possessions cluster in
  particular score-time states. Include score-margin and period controls
  in the stint regression (or verify the RAPM residualization already
  absorbs this — check, don't assume).
- Keep the hiding-baked-in framing: κ_i is the *net observed* effect
  including coach protection. That's the decision-relevant quantity.

---

## Phase C — Identification notes (write these into the paper as built)

1. **Selection into the sample:** coaches choose who plays through foul
   trouble; disciplined/trusted players are overrepresented. The player
   main-effect column absorbs level selection; κ_i is identified from
   within-player variation. But the *set of players with any foul-trouble
   minutes* is still selected — κ_i for players coaches never leave in is
   extrapolation from the prior. Say so.
2. **Reporting threshold:** publish individual κ_i only for players above
   the Phase A possession threshold; everyone else is reported as
   "group-level estimate." No fake precision.
3. κ̄ from this specification should reconcile with the v1 pooled estimate
   (minutes-weighted average of κ_i ≈ κ̄, and the global column ≈ old
   pooled coefficient). If it doesn't, the specification changed something
   unintended — stop and diagnose.

---

## Phase D — Validation (extends TEST_CASES.md; all must pass before DP integration)

- **C3 goes live:** scatter κ_i vs. foul-trouble possessions. Thin-sample
  players hug the group mean; dispersion widens with data. Extreme κ from
  thin samples = pooling broken.
- **Reconciliation:** minutes-weighted mean of κ_i vs. pooled κ̄ (above).
- **Out-of-sample gate (the important one):** held-out season or held-out
  stints — does per-player κ_i predict foul-trouble stint outcomes better
  than pooled κ̄? Report the improvement, even if ≈ 0. This is the honest
  measure of how much player heterogeneity the data supports.
- **Face validity:** the most-negative reliable κ_i and least-negative —
  do they pass a basketball smell test? (No strong priors here; treat as
  inspection, not pass/fail.)
- **DP integration check:** rerun thresholds + headline with κ_i.
  Headline should move modestly; threshold maps should now differ across
  players with similar δ, λ but different κ — that differentiation is the
  new content. Log old-vs-new headline in VALIDATION.md.

---

## Phase E — The claims decision (closes the positioning gap)

Three outcomes, all publishable — decide the paper language based on which
occurs:

1. **Real heterogeneity** (out-of-sample gain > 0, some κ_i intervals
   separate from κ̄): full "player-specific κ" claim restored; personalized
   maps genuinely personalized on all three parameters.
2. **Weak heterogeneity** (shrinkage pulls nearly everyone to the group
   mean, OOS gain ≈ 0): claim becomes "we tested for player-specific
   playing-scared effects; the data supports group-level effects with
   limited individual variation." Still a finding — arguably a cleaner
   one — and personalization rests on δ and λ, which is defensible.
3. **Group heterogeneity only** (groups differ, individuals within don't):
   "archetype-specific κ" — fits the paper's archetype framing neatly.

**Hard rule:** the abstract's claims match whichever outcome the data
delivers. The current mismatch (paper says player-specific, model is
pooled) must be resolved by this phase, before the abstract draft.

---

## Sequencing within PROJECT_PLAN

- Phase A can run the moment expanded data passes the validation gate
  (end of PROJECT_PLAN Phase 1) — it's one tabulation.
- Phases B–D are PROJECT_PLAN Phase 2 work (~1.5 weeks of the robustness
  window). The λ_κ cross-validation is the slow part; everything else
  reuses the RAPM pipeline.
- Phase E deadline: before the abstract draft starts (Aug 31).
- If the expansion slips or Phase A shows hopeless sparsity: fall back to
  outcome-3 language early (group-level κ by archetype), skip per-player
  columns, and bank the time. That fallback is decided at the end of
  Phase A, not mid-build.

## Definition of done

κ_i (or group κ) estimated with documented shrinkage; C3 plot in
VALIDATION.md; OOS comparison logged; REFERENCE.md notation pinned;
headline re-run; paper claims updated to match the data's verdict;
committed and tagged `kappa-v2`.
