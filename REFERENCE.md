# Foul Budget Management in the NBA
### Quantifying the Win Probability Cost of Conventional Foul-Trouble Benching

**Target:** MIT Sloan Sports Analytics Conference (SSAC27) Research Paper Competition
**Abstract deadline:** October 1, 2026 · **Full paper (if selected):** December 4, 2026
**Requirement:** Paper and code must be open-source.
**Author context:** Computer engineering student and head coach of a university basketball team. The coaching background is a framing and validation angle: these are real decisions the author makes from the bench.

---

## 1. Research Question

When a valuable player picks up early fouls, nearly every coach benches him ("fouls ≥ quarter + 1, he sits"). Is this convention optimal? We quantify the expected win probability cost of conventional foul-trouble benching versus a policy derived from a dynamic decision model.

**Headline deliverable:** one number — e.g., "conventional benching costs ~X% win probability per occurrence, roughly Y wins per team per season" — plus personalized play/sit threshold maps by player profile.

**Positioning — adjudicating a live dispute, not extending settled work:**
- **Maymin, Maymin & Shen (SSAC 2012, IJSF)** framed foul trouble as strategically idling resources and concluded starters *ought* to be benched on a Q+1 basis when future option value or replacement value is high. They largely defended the convention. They also hypothesized (but did not estimate) the "playing scared" mechanism: players expecting to be yanked may rationally play tentatively.
- **Moskowitz & Wertheim (Scorecasting, 2011)** found the opposite: stars play *better* in the fourth quarter while carrying foul trouble, implying benching is a mistake.
- These findings have stood in unresolved contradiction since 2012. This paper adjudicates the dispute with ~10x the data and better methods.
- **Supporting prior evidence for γ₁ < 0:** independent analysis of 2016–19 play-by-play found players commit ~40% fewer fouls when in foul trouble (with ~16% fewer blocks, suggesting avoidance of foul-risk situations; referee make-up calls may also contribute). The adaptation effect is documented but has never been embedded in a decision model.
- **This paper's gap:** nobody has combined (a) an adaptive foul hazard, (b) an explicitly *estimated* effectiveness discount κ (Maymin et al. theorized it; we measure it), and (c) backward-induction policy comparison in one framework. Maymin et al.'s "option value" argument is not assumed here — it is tested directly via the leverage term ∂W/∂d, which quantifies whether late minutes are actually worth saving for.
- Adjacent citations: McFarlane (2019) end-of-game tactics metric (different decision, methodological kinship); inpredictable's intentional-fouling work (different problem).

Novelty is in the decision framing and the adjudication (coaching behavior, real stakes), not exotic methodology.

### Related Work

**Closest prior work — the paper we are adjudicating against:**
- Maymin, Maymin & Shen (2012), "How Much Trouble is Early Foul Trouble? Strategically Idling Resources in the NBA," *International Journal of Sport Finance* 7:4, 324–339 (originally SSAC 2011; free PDF on SSRN abstract 1736633 and the Sloan site). Build a win-probability model on 2006–09 play-by-play and conclude benching foul-troubled starters (Q+1) is generally correct. They propose a "playing scared" effect as a possible mechanism but never estimate it as an identified parameter — we estimate κ. Do not let this paper's framing drift into "first to study foul trouble."

**Directly relevant methodology:**
- Chu & Swartz, "Foul Accumulation in the NBA" (SFU, free PDF: sfu.ca/~tswartz/papers/foul.pdf). Bayesian gamma model of fouling times; finds foul hazard **increases with current foul count** — informs the Cox/Poisson hazard spec (foul count as covariate/stratum, not just exposure). Uses hierarchical partial pooling for player-level parameters — precedent for our κ estimation strategy.

**The anti-benching side (theory, no empirical model):**
- Weinstein (2010), *Leisure of the Theory Class* blog: benching never increases expected minutes; post-bench minutes distribution is a truncation of the no-bench distribution.
- Moskowitz & Wertheim, *Scorecasting* (book).

**Secondary / practitioner (shows the debate is still live post-2012):**
- Falk (2018), "The Trouble with Foul Trouble," Cleaning the Glass (paywalled — cite via Chu & Swartz's characterization). Covers foul management strategies incl. defensive reassignment → relevant to the hiding-as-limitation section.
- Klobuchar (2018), blog analysis of win-share inefficiency from early foul substitutions.
- Hoop Vision Substack (2024), "Foul Trouble & The Auto-Bench" — Pomeroy data: starters with 2 first-half fouls play only ~23% of remaining first-half minutes (college, but evidence the convention is alive and contested).

**Gap statement:** No prior work combines player-specific (δ, λ, κ) parameterization, backward-induction DP, and an *empirically estimated* playing-scared discount into personalized play/sit thresholds and a league-wide win-probability cost of the Q+1 convention; nobody has revisited the question with post-2012 data despite a live practitioner debate.

---

## 2. Model Specification (LOCKED — do not add actions)

### State
`s = (t, d, f)` — time remaining, score differential, player's current foul count. Player identity enters through parameters `(δ_i, λ_i, κ_i)`, solved over a grid of parameter combinations so any player maps to a point on the surface.

### Actions
Two actions only: **play** or **sit**.

```
V(s) = max{ V_play(s), V_sit(s) }
```

- `V_play`: score drifts at the player's (discounted) net rate `δ' = δ − κ` while fouls accrue at hazard `λ`; reaching f = 6 locks in backup drift for the remainder.
- `V_sit`: score drifts at backup rate; no foul risk.
- Terminal condition: `V(0, d, ·) = 1[d > 0]`.
- Solve by backward induction on a discretized grid (≈30s time steps, score diff −30..+30, fouls 0–6).

### Explicitly OUT of scope (documented limitation, not a feature)
A third "hide" action (defensive reassignment onto weaker offensive players) is **excluded**. Rationale: coaches already hide foul-troubled players, so hiding is baked into the observational data. Therefore:
- Estimated `γ₁` (foul-rate adaptation) = combined effect of player caution + coach hiding.
- Estimated `κ` = the all-in net cost of keeping a foul-troubled player on court *as coaches currently manage them*.
- This makes "play" = "keep him on and manage as NBA coaches currently do," which is the decision-relevant comparison. It also strengthens any anti-benching result.
- Limitations paragraph should note: decomposing player adaptation vs. tactical reassignment requires defensive matchup / tracking data (future work).

---

## 3. Estimation Plan

### 3.1 Win probability backbone
`W(d, t) = P(win | score diff d, time remaining t)`.
Logistic with `d`, `d/√t`, `t` fit on the behavioral window (§4 two-window design); nonparametric bin-and-count table kept as a calibration check. Key derived quantity: leverage `∂W/∂d`, which converts point value into win probability and is often *larger* in close 2nd quarters than blowout 4th quarters — this undercuts the "save him for later" intuition.

### 3.2 Player value

**Impact metric: RAPM**, computed via ridge regression on our own stint-level plus-minus data (not third-party published RAPM — the SSAC open-source requirement means the pipeline must reproduce it end-to-end).

**Primary definition:**
```
delta_i = RAPM_i − Σ_j w_ij · RAPM_j
```
where `w_ij` = minutes-weighted share of player i's replacement minutes absorbed by player j (the "empirical replacement composite"), per player per season. RAPM is measured vs. league average; backups are mostly below average, so raw RAPM (vs. league average) understates the play/sit gap.

**Robustness check:** `delta_i = RAPM_i` (vs. league average). This biases *against* the likely headline (makes benching look cheaper), so it's the conservative spec — if benching still looks costly here, the result is robust.

**Replacement distribution construction:**
- Built directly from play-by-play substitution events ("Player B replaces Player A"), counted and minutes-weighted per player per season. Source: shufinskiy/nba_data + pbpstats for cleaning; a groupby on sub events *after* stint reconciliation passes.
- Refinement (implement if data supports it): condition weights on foul-trouble substitutions specifically (outgoing player at fouls ≥ Q+1 when subbed), since foul-trouble replacements may differ from rest replacements.
- Sample-size fallback: players with few observed foul-trouble subs fall back to the overall substitution distribution, then position-based replacement — same partial-pooling spirit as κ (§3.4).
- Known limitations (document, don't fix in v1): mass substitutions make the scorer's A-out/B-in pairing positionally arbitrary (acceptable noise, smoothed by minutes-weighting); the entering player isn't always the positional replacement (lineup slides) — do not chase lineup-role inference in v1.
- Framing note: because the composite reflects *observed coach behavior*, the counterfactual is "play him vs. what coaches demonstrably do instead" — consistent with the hiding-baked-in argument (§2), and the WP cost evaluates the real decision coaches face.

### 3.3 Foul hazard (core modeling work)
**Exposure table:** decompose games into player-stint windows. Each row = (player, minutes exposed, current foul count, period, score margin, opponent, fouls committed in window). New row on any state change.

**Primary model — Poisson regression with exposure offset:**
```
log E[fouls_iw] = log(minutes_iw)          # offset, no coefficient
               + α_i                        # player baseline (shrink low-minute players toward position mean)
               + γ₁ · foulcount_iw          # adaptation term — expected NEGATIVE
               + γ₂ · X_iw                  # period, margin, home/away, opp FT-draw rate, rest
```
Coefficients read as % changes via exp().

**Robustness — Cox proportional hazards** on time-to-next-foul with censoring at sub-out/game end; flexible baseline `λ₀(t)` captures within-game timing patterns. Stratify (or include as a covariate) by current foul count, not just Poisson's γ₁ — Chu & Swartz (see Related Work) find foul hazard increases with current foul count independent of the adaptation effect, so the Cox spec needs a foul-count-dependent hazard rather than a constant per-player rate. Poisson and Cox should broadly agree; report both.

**Key empirical claims to establish:**
1. `γ₁ < 0` — players in foul trouble foul less (self-regulation). Prior independent work found ~-40% foul rate in foul trouble; replicate at scale with proper exposure/controls. Coaches implicitly assume constant hazard, overestimating foul-out risk.
2. Killer validation chart: model-based foul-out probability vs. constant-hazard foul-out probability for a star at 3 fouls in Q2 (e.g., 18% real vs 35% feared).
3. κ estimated, not theorized — this is what separates the paper from Maymin et al. (2012), who proposed the tentative-play mechanism but never measured it. Whether κ is large (vindicating Maymin's pro-benching result) or small (vindicating Scorecasting's anti-benching result) is the adjudication.

### 3.4 "Playing scared" discount κ

**Notation (pinned, per HIERARCHICAL_KAPPA_PLAN.md):** κ_i is player i's
foul-trouble performance *deviation*, in RAPM units (points/100 possessions;
≈ points/48 at league pace, and points/min = points/48 ÷ 48 internally).
κ_i = 0 means no playing-scared effect; negative = plays worse in foul
trouble. The pooled v1 estimate is κ̄ (currently +4.2 per 48 on the 5-season
window, i.e. positive: players outperform their baseline in foul trouble as
currently managed).
Per-player κ_i (v2, src/hazard/kappa_v2.py) is estimated: league-wide
partial pooling (Phase A rejected tier grouping on 5 seasons), ridge
deviations with λ_κ by CV. Verdict = HIERARCHICAL_KAPPA_PLAN Phase E
outcome 2: out-of-sample gain of κ_i over pooled κ̄ ≈ +0.03% of held-out
MSE — the data supports a pooled playing-scared effect with limited
individual variation. Paper claims use group-level κ language;
personalization rests on δ_i and λ_i. The DP keeps pooled κ̄.

```
net_rating_it = θ_i + κ · 1[foul_trouble_it] + controls + ε
```
Foul trouble defined as fouls ≥ quarter + 1. Include player fixed effects and opponent controls. Report κ as an upper bound on the causal effect (foul trouble is not randomly assigned). Either result publishable: large κ partly vindicates convention; small κ means coaches burn wins.

**Estimation:** per-player independent κ is infeasible — foul-trouble stints are rare, and many rotation players log only a handful of foul-trouble minutes per season. Use hierarchical partial pooling: each player's κ shrunk toward a group-level estimate (group by position, role, or foul-rate tier — pick after seeing foul-trouble stint counts per player); heavily-observed players keep their own signal, thin-sample players lean on the group (precedent: Chu & Swartz). Describe in the paper as "player-level parameterization, hierarchically estimated."

### 3.5 Policy comparison (headline)
```
Cost of convention = E_real_states[ V^π*(s) − V^πc(s) ]
```
where π* = model-optimal policy, πc = conventional benching rule. Evaluate over actual foul-trouble states observed in held-out seasons. Also run per-player-archetype: expect **starting centers** (high λ, weak backups, defensive anchors) to be a bigger leak than wing stars — underexplored angle.

**Open questions (resolve during estimation, not before):**
- RAPM regularization: single-season vs. multi-season prior? (Multi-season stabilizes δ but complicates per-season replacement composites.)
- κ pooling group: RESOLVED (2026-07-15) — league-wide; foul-rate and minutes tiers do not separate on 5 seasons (reports/kappa_audit.md).
- Threshold for the "few observed foul-trouble subs" fallback (§3.2) — set empirically once sub events are tabulated.

---

## 4. Data Sources (in priority order)

### Two-window design (DECIDED 2026-07-14 — supersedes the earlier "full 20+ seasons" plan)

- **Behavioral analysis window — 2021-22 through 2025-26 only** (seasons `2021`–`2025` in shufinskiy numbering). Everything behavioral runs exclusively here: κ, λ, the foul hazard, the DP, decision analysis, and the headline. Rationale: one officiating regime (post the 2021 non-basketball-move foul rule change), no bubble/COVID-shortened seasons.
- **RAPM ingestion window — 2019-20 onward** (seasons `2019`–`2025`). 2019-20 and 2020-21 are **decay burn-in only**: their stints feed the half-life-weighted ridge so early analysis seasons have a warm prior, but no ratings are reported for them and they are never analysis seasons.
- Enforced in code by `src/config.py` (`ANALYSIS_SEASONS`, `BURNIN_SEASONS`, `RAPM_SEASONS`); no module hardcodes a season list. The W(d,t) backbone also fits within the behavioral window (same officiating-regime logic; the 5-season logistic is well-fed, the nonparametric table stays a secondary check).

1. **shufinskiy/nba_data** (GitHub) — pre-scraped play-by-play from stats.nba.com, data.nba.com, pbpstats.com, 1996–present. Bulk download; primary corpus (windows above).
2. **eightthirtyfour.com/data** — play-by-play with on-court lineups already derived; possession tracking included; free for academic use. Cross-check against #1.
3. **pbpstats** (Python package, Darryl Blackport) — lineup validation, possession logic, fixes misordered/missing substitution events. Primary parsing tool.
4. **nba_api** — gap-filling only.
5. Player value: public EPM/RAPTOR archives, or self-built RAPM from the lineup data.

**Do NOT use:** Basketball Reference scraping (ToS + no bulk), Cleaning the Glass (aggregated, paywalled, no raw events).

---

## 5. Known Traps

- **Substitution parsing:** raw NBA pbp has missing/misordered sub events. Two repairable corruption modes (both fixed in `src/ingest/lineups.py:_repair_event_order`): isolated mislabeled PERIOD values, and real events carrying corrupt EVENTNUMs that strand them out of position (~370 sub rows across ~200 games per 3 seasons). A handful of games (~5 per 3 seasons) have wholesale-corrupt sub ledgers no reordering can repair — dropped explicitly via `lineups.CORRUPT_GAMES` (pbpstats/data.nba.com live repair endpoints are unreachable from the build machine; eightthirtyfour.com is the fallback source if those games ever matter). Validate stint minutes against official box score minutes per player per game before trusting anything downstream: `check_team_minutes.py` (free, full-corpus physical-total screen) then `validate_minutes.py` (sampled box-score gate with forced regression games).
- **Selection bias in γ₁:** minutes at high foul counts are coach-selected, not random. Player fixed effects handle between-player selection; state clearly that γ₁ is conditional on current deployment practices (which is the decision-relevant rate).
- **Referee heterogeneity:** crews vary in whistle tightness. Add crew random effect or game-level foul-rate control.
- **Endogeneity of κ:** foul trouble correlates with tough matchups; control for opponent, report as bound.
- **Scope creep:** resist modeling individual foul *types*, hiding, or tracking-data extensions. One clean number beats three muddy ones.

---

## 6. Validation

- Hold out ≥1 full season. Predicted vs. actual fouls in buckets (player type × foul count × quarter).
- Calibration of W(d,t) on held-out games.
- Policy cost evaluated only on held-out foul-trouble states.
- Coaching sanity check: qualitative comparison of model thresholds against author's own bench decisions (framing/validation section, not quantitative evidence).

---

## 7. Timeline

| Window | Milestone |
|---|---|
| July (weeks 1–2) | Data download, pbpstats pipeline, exposure table built and validated against box scores |
| July (weeks 3–4) | W(d,t) backbone + δ values assembled |
| Early August | Poisson hazard fit; γ₁ established; Cox robustness |
| Mid–late August | κ regression; backward-induction solver; policy comparison; headline number |
| Early September | Validation charts, per-archetype results, sensitivity checks |
| Mid September | Abstract drafted (≤2 weeks buffer before Oct 1) |

---

## 8. Repo Conventions

- Python. Suggested layout: `data/` (gitignored raw), `src/ingest/`, `src/hazard/`, `src/wp/`, `src/policy/`, `notebooks/` (exploration only, logic lives in src), `tests/`.
- Everything must be reproducible end-to-end (SSAC open-source requirement): one `make all` or `run.py` from raw download to headline number.
- Validate each pipeline stage before building the next (esp. stint minutes vs. box scores — do this FIRST).
- Writing style note for any prose/abstract drafts: do not use dashes as mid-sentence punctuation.

## 9. Immediate Next Steps

1. `pip install pbpstats nba_api statsmodels lifelines`
2. Download the §4 two-window corpus from shufinskiy/nba_data (behavioral 2021–2025, burn-in 2019–2020). [dev slice of 3 seasons completed first]
3. Build stint/exposure table for the dev slice.
4. **Validation gate:** per-player per-game stint minutes must reconcile with official box scores before any modeling.
5. Replacement distributions (§3.2) and RAPM both consume the reconciled stint data — build them immediately after the gate passes.
