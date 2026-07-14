# TEST_CASES.md — Verification suite for the foul-trouble model
## Each case states the setup and the output you should see. If you don't, something is wrong — no exceptions are "close enough" unless noted.

---

## A. Degenerate parameter tests (feed the DP synthetic players)

These test the decision logic in isolation. Create synthetic players with
hand-set (delta, lambda, kappa) and run the DP. No real data involved.

**A1. No playing-scared effect: kappa = 1 (no discount)**
Expected: the DP should essentially NEVER bench purely for foul trouble.
This is Weinstein's theorem — with two actions and no performance discount,
sitting a player can only truncate his minutes, never extend them. The
threshold map should read "play" everywhere (except after fouling out).
If the model benches anyone with kappa = 1, the DP has a bug.

**A2. Worthless player: delta = 0**
Expected: WP cost of the Q+1 convention ≈ 0 for this player. Benching him
is free — the replacement is exactly as good. Decision maps may be
indifferent; the COST must be ~0.

**A3. Never fouls: lambda = 0**
Expected: always play. No foul-out risk means no option value to preserve.

**A4. Extreme playing-scared: kappa discount so large that foul-trouble
delta goes negative** (player in foul trouble is WORSE than his backup)
Expected: model recommends benching aggressively — this should reproduce
Maymin-style pro-benching behavior. Confirms the mechanism runs both ways.

**A5. Monotonicity sweep**
Vary one parameter at a time on a grid, hold others fixed:
- Higher delta → thresholds shift toward "play" (never the reverse)
- Higher lambda → thresholds shift toward "sit" earlier
- Stronger kappa discount → thresholds shift toward "sit"
Any non-monotone flip on the grid = bug (or a genuinely interesting
interaction — inspect before dismissing, but expect bug).

---

## B. Boundary conditions (DP structure)

**B1. End of game: t → 0**
Expected: with little time remaining, benching is never optimal for any
parameter combo — there is no future to save the player for. In the last
~2 minutes the policy should say "play" for every player with delta > 0,
even at 5 fouls. If the model sits anyone at t = 30 seconds, the backward
induction is mis-indexed.

**B2. Foul-out absorbing state**
Expected: at 6 fouls the player is unavailable in every subsequent state;
value function must use replacement value from that point on, no leakage.

**B3. Blowouts: |score margin| very large**
Expected: WP cost of any decision ≈ 0 (W(d,t) is saturated at ~0 or ~1).
If foul decisions move win probability in a 30-point game, the W(d,t)
backbone is miscalibrated in the tails.

**B4. Symmetry of the backbone**
W(d, t) + W(−d, t) ≈ 1 for all margins and times (up to home-court
handling — if W is home-team-based, check the reflection accordingly).

---

## C. Data & estimation invariants (real data, automatic checks)

**C1. Replacement composite weights sum to 1** for every player-season.

**C2. Optimal-policy dominance: WP cost ≥ 0 for EVERY player.**
The cost is defined as optimal policy minus Q+1 convention. The optimal
policy cannot be worse than the convention it contains as a special case.
A single negative cost anywhere = bug in the policy evaluation.

**C3. Shrinkage behaves:** plot per-player kappa vs. foul-trouble minutes
observed. Low-minute players must cluster near their group mean;
dispersion should widen with sample size. If thin-sample players show the
most extreme kappas, pooling is broken.

**C4. Hazard face-check:** total predicted fouls per player-season from
the hazard model should reconcile with actual box-score foul totals
(within a few percent, aggregated).

**C5. RAPM benchmark:** in-house 3-year RAPM vs. nbarapm.com same-window
values, r ≳ 0.9. (Already planned — listed here so the suite is complete.)

---

## D. Literature reproduction (the most persuasive test you can run)

**D1. Recover Maymin et al. under their assumptions.**
Set kappa to a strong discount (their implied playing-scared magnitude)
and generic league-average-ish delta/lambda, run the DP.
Expected: pro-benching thresholds close to the Q+1 convention — i.e.,
their conclusion falls out of your machinery under their assumptions.
This is the single best slide in the eventual talk: "their result is a
special case of our model at a kappa the data rejects."

**D2. Recover Scorecasting/Weinstein at kappa = 1** (same as A1, but frame
it this way in the paper: the anti-benching position is also a special
case — at the other end of the kappa axis. Your estimated kappa locates
the league between the two, and the DP adjudicates.)

---

## E. Face-validity spot checks (real players, eyeball tests)

**E1. Archetype ordering.** Rank players by modeled WP cost of the
convention. The top should be dominated by high-delta, high-lambda,
weak-backup players — foul-prone starting centers and heliocentric stars
with thin benches. If the most expensive player to auto-bench is a
low-minute wing, inspect.

**E2. Known foul-prone stars vs. known low-foul stars.** Pull the
lambda estimates and check them against reputation: foul-prone bigs
should carry visibly higher lambda than famously foul-disciplined stars.
Cross-check a handful against per-36 foul rates from box scores — the
ordering must agree.

**E3. Strong-backup discount.** Find 2–3 stars whose teams have
well-regarded backups at the same position and confirm their delta (and
hence their benching cost) is visibly smaller than comparable stars with
weak backups. The model should "know" that benching costs depend on the
bench.

**E4. Self-mined case studies.** Query your own data for the games with
the largest realized WP cost: starter in top-decile delta sat ≥ X minutes
while at Q+1, game decided by ≤ 5 points. Read the play-by-play for the
top 3 hits and check the story makes basketball sense (close game, star
glued to bench in a swing period, team bleeding margin during the sit).
These become the paper's case studies, so this test does double duty.

**E5. One full game trace.** Pick a single game, print the model's
recommended action at every foul-trouble decision point alongside what
the coach did, minute by minute. Read it like a coach. Anything that
looks insane (sit a star in a tie game with 3 minutes left) is either a
bug or the most interesting paragraph in the paper — determine which.

---

## Suggested run order

1. A1–A5, B1–B4 (synthetic, fast, catches DP bugs before real data
   confuses things)
2. C1–C5 (data invariants)
3. D1–D2 (literature endpoints)
4. E1–E5 (eyeball tests, produces paper material)

Log every result — pass/fail plus the artifact (plot, table, trace) — in
a VALIDATION.md. The open-source reviewers get this file too; a visible
falsification suite is rare in SSAC submissions and reads as rigor.
