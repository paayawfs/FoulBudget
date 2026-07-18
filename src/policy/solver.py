"""Backward-induction play/sit solver per REFERENCE.md Section 2 (LOCKED).

State s = (t, d, f): 30s time steps over regulation, score diff -30..+30 from
the focal team's perspective, player fouls 0..6. Two actions:

    V(s) = max{ V_play(s), V_sit(s) }

  - sit: margin evolves by the empirical league 30s margin-step distribution
    (player replaced by his composite backup -- delta is measured vs exactly
    that composite, so sit-drift is the zero point).
  - play: same distribution shifted by drift = delta + kappa*1[foul trouble];
    fouls arrive at hazard lambda(f, period); f = 6 locks in sit forever.
  - terminal: V(0, d) = 1[d > 0] + 0.5*1[d = 0].

The conventional policy pi_c (sit iff f >= period + 1) is valued on the same
dynamics; cost of convention = V* - V^c averaged over foul-trouble states
actually observed in the held-out season's exposure table (Section 3.5).

ponytail: margin steps are state-independent (no leverage-dependent pace/
variance) and home advantage is ignored (symmetric-perspective W); both are
second-order for a policy DIFFERENCE. Revisit for the paper's sensitivity
section.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
LINEUPS_DIR = ROOT / "data" / "processed" / "lineups"
EXPOSURE_DIR = ROOT / "data" / "processed" / "exposure"
HAZARD_DIR = ROOT / "data" / "processed" / "hazard"
VALUE_DIR = ROOT / "data" / "processed" / "value"

STEP_SECONDS = 30
N_STEPS = 2880 // STEP_SECONDS          # 96
# lattice extends past the +-30 decision region so that transition clipping
# (which manufactures mean reversion at the edge) distorts only a buffer zone;
# edge values are pinned to 0/1 every step (absorbing blowouts)
D_MAX = 45
D_GRID = np.arange(-D_MAX, D_MAX + 1)   # 91
N_FOULS = 7                              # 0..6
PLAY_TIE_EPS = 1e-12                     # indifference resolves to play
import sys as _sys
_sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import ANALYSIS_SEASONS, EVAL_SEASON
TRAIN_SEASONS = tuple(s for s in ANALYSIS_SEASONS if s != EVAL_SEASON)


def margin_step_distribution() -> np.ndarray:
    """Empirical distribution of home-margin change over 30s, league-wide."""
    frames = []
    for s in TRAIN_SEASONS:
        df = pd.read_parquet(LINEUPS_DIR / f"{s}.parquet",
                             columns=["GAME_ID", "PCTIMESTRING", "SCOREMARGIN"])
        df["margin"] = pd.to_numeric(df["SCOREMARGIN"].replace("TIE", "0"), errors="coerce")
        df["margin"] = df.groupby("GAME_ID")["margin"].ffill().fillna(0)
        frames.append(df[df["PCTIMESTRING"] <= 2880])
    df = pd.concat(frames, ignore_index=True)

    grid = np.arange(0, 2881, STEP_SECONDS)
    steps = []
    for _, g in df.groupby("GAME_ID"):
        m = np.interp(grid, g["PCTIMESTRING"], g["margin"])
        steps.append(np.diff(np.round(m)))
    steps = np.concatenate(steps).astype(int)

    lo, hi = steps.min(), steps.max()
    counts = np.bincount(steps - lo)
    support = np.arange(lo, hi + 1)
    # de-mean so the sit action is drift-free by construction
    probs = counts / counts.sum()
    mean = (support * probs).sum()
    return support, probs, mean


def expected_over_margin(V_next: np.ndarray, support, probs, shift: float) -> np.ndarray:
    """E[V(t-1, d + step + shift)] for every d; linear interp on the d grid."""
    ev = np.zeros_like(V_next)
    for k, p in zip(support, probs):
        d_new = np.clip(D_GRID + k + shift, -D_MAX, D_MAX)
        ev += p * np.interp(d_new, D_GRID, V_next)
    return ev


def period_of_step(t_step: int) -> int:
    """NBA period at time-remaining index t_step (t_step*30s remaining)."""
    elapsed = 2880 - t_step * STEP_SECONDS
    return min(4, elapsed // 720 + 1) if elapsed < 2880 else 4


def hazard_table(gammas: pd.DataFrame) -> np.ndarray:
    """multiplier[f, period] on the player's base rate, from the dummies spec."""
    g = gammas[gammas["spec"] == "dummies"].set_index(gammas.columns[0])["coef"]
    mult = np.ones((N_FOULS, 5))
    for f in range(N_FOULS):
        fc = g.get(f"fc_{min(f, 5)}", 0.0) if f > 0 else 0.0
        for p in (1, 2, 3, 4):
            pp = g.get(f"p_{p}", 0.0) if p > 1 else 0.0
            mult[f, p] = np.exp(fc + pp)
    return mult


class PolicyValues:
    """Backward induction over the (t, f, d) lattice; stores V*, V^c, and
    the optimal action (policy[t, f, d] = 1 means play)."""

    def __init__(self, delta, lam_base, kappa, support, probs, mean_step,
                 terminal="wp"):
        mult = hazard_table(pd.read_csv(HAZARD_DIR / "gammas.csv"))
        shift_sit = -mean_step  # de-meaned noise: sit is drift-free
        if terminal == "linear":
            # constant-leverage terminal value: the Weinstein/A1 test world
            term_row = (D_GRID + D_MAX) / (2 * D_MAX)
        else:
            term_row = (D_GRID > 0) + 0.5 * (D_GRID == 0)
        term = np.tile(term_row, (N_FOULS, 1)).astype(float)
        self.V_opt = np.empty((N_STEPS + 1, N_FOULS, len(D_GRID)))
        self.V_conv = np.empty_like(self.V_opt)
        self.policy = np.zeros((N_STEPS + 1, N_FOULS, len(D_GRID)), dtype=np.int8)
        self.V_opt[0] = term
        self.V_conv[0] = term

        for t in range(1, N_STEPS + 1):
            period = period_of_step(t)
            for f in range(N_FOULS):
                ev_sit_o = expected_over_margin(self.V_opt[t - 1, f], support, probs, shift_sit)
                ev_sit_c = expected_over_margin(self.V_conv[t - 1, f], support, probs, shift_sit)
                if f == 6:
                    self.V_opt[t, f] = ev_sit_o
                    self.V_conv[t, f] = ev_sit_c
                    continue
                in_trouble = f >= period + 1
                drift = (delta + (kappa if in_trouble else 0.0)) * STEP_SECONDS / 60
                lam = lam_base * mult[f, period]
                p_foul = 1 - np.exp(-lam * STEP_SECONDS / 60)
                ev_play_o = (1 - p_foul) * expected_over_margin(self.V_opt[t - 1, f], support, probs, shift_sit + drift) \
                    + p_foul * expected_over_margin(self.V_opt[t - 1, f + 1], support, probs, shift_sit + drift)
                ev_play_c = (1 - p_foul) * expected_over_margin(self.V_conv[t - 1, f], support, probs, shift_sit + drift) \
                    + p_foul * expected_over_margin(self.V_conv[t - 1, f + 1], support, probs, shift_sit + drift)
                play = ev_play_o >= ev_sit_o - PLAY_TIE_EPS
                self.policy[t, f] = play
                self.V_opt[t, f] = np.where(play, ev_play_o, ev_sit_o)
                self.V_conv[t, f] = ev_play_c if f < period + 1 else ev_sit_c
            # pin absorbing blowout edges (consistent with either terminal)
            self.V_opt[t, :, 0] = term[:, 0]
            self.V_opt[t, :, -1] = term[:, -1]
            self.V_conv[t, :, 0] = term[:, 0]
            self.V_conv[t, :, -1] = term[:, -1]

    def lookup(self, which, t_remaining, f, d):
        t_idx = int(np.clip(round(t_remaining / STEP_SECONDS), 0, N_STEPS))
        V = self.V_opt if which == "opt" else self.V_conv
        return float(np.interp(np.clip(d, -D_MAX, D_MAX), D_GRID, V[t_idx, min(f, 6)]))


def evaluate_convention_cost(support, probs, mean_step, kappa: float) -> pd.DataFrame:
    """V* - V^c at the first observed foul-trouble state per player-game."""
    exp_df = pd.read_parquet(EXPOSURE_DIR / f"{EVAL_SEASON}.parquet")
    exp_df = exp_df[exp_df["minutes_exposed"] > 0]
    trouble = exp_df[exp_df["foul_count"] >= exp_df["period"] + 1]
    first = trouble.sort_values("start_elapsed").groupby(["game_id", "player_id"]).first().reset_index()

    delta = pd.read_csv(VALUE_DIR / f"delta_{EVAL_SEASON}.csv")
    delta = delta.dropna(subset=["delta"]).set_index("player_id")
    alphas = pd.read_csv(HAZARD_DIR / "alphas.csv", index_col=0)["alpha"]

    first["delta"] = first["player_id"].map(delta["delta"])
    first["minutes"] = first["player_id"].map(delta["minutes"])
    first["lam"] = np.exp(
        first["player_id"].astype(str).add(f"_{EVAL_SEASON}").map(alphas)
    )
    first = first.dropna(subset=["delta", "lam"])
    first = first[first["minutes"] >= 500]  # rotation players only

    # solve once per (delta, lam) cell on a coarse parameter grid
    first["d_cell"] = first["delta"].clip(-0.05, 0.20).round(2)
    first["l_cell"] = first["lam"].clip(0.02, 0.16).round(2)

    rows = []
    for (dc, lc), grp in first.groupby(["d_cell", "l_cell"]):
        pv = PolicyValues(dc, lc, kappa, support, probs, mean_step)
        for _, r in grp.iterrows():
            sign = 1.0 if r["side"] == "HOME" else -1.0
            d_team = sign * r["score_margin"]
            t_rem = 2880 - min(r["start_elapsed"], 2880)
            gap = (pv.lookup("opt", t_rem, int(r["foul_count"]), d_team)
                   - pv.lookup("conv", t_rem, int(r["foul_count"]), d_team))
            rows.append({
                "game_id": r["game_id"], "player_id": r["player_id"],
                "team": r["team"],
                "delta": r["delta"], "foul_count": int(r["foul_count"]),
                "period": int(r["period"]), "cost_wp": gap,
            })
    return pd.DataFrame(rows)


def run() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    support, probs, mean_step = margin_step_distribution()
    print(f"margin-step support {support.min()}..{support.max()}, "
          f"mean {mean_step:+.4f} (de-meaned for the DP)")

    kappa = pd.read_csv(HAZARD_DIR / "kappa.csv", index_col=0).loc["foul_trouble", "coef"]

    # threshold map for a representative star (delta ~ +6/48, league-avg hazard)
    star = PolicyValues(delta=6 / 48, lam_base=0.055, kappa=kappa,
                        support=support, probs=probs, mean_step=mean_step)
    d0 = len(D_GRID) // 2  # tied game
    print("\nplay(1)/sit(0) at d=0 for star (delta=+6/48, lam=2.6/48): "
          "rows = fouls 1-5, cols = start of Q1..Q4")
    q_steps = [96, 72, 48, 24]  # t indices at quarter starts
    for f in range(1, 6):
        print(f"  f={f}: ", [int(star.policy[t, f, d0]) for t in q_steps])

    for k_label, k_val in (("estimated kappa", kappa), ("kappa = 0 (conservative)", 0.0)):
        costs = evaluate_convention_cost(support, probs, mean_step, k_val)
        occ = costs["cost_wp"]
        per_team_season = occ.sum() / 30
        print(f"\n=== cost of convention, {k_label} ===")
        print(f"foul-trouble occurrences ({EVAL_SEASON}): {len(costs):,}")
        print(f"mean WP cost per occurrence: {occ.mean() * 100:.2f}pp | "
              f"median {occ.median() * 100:.2f}pp | p90 {occ.quantile(0.9) * 100:.2f}pp")
        print(f"implied wins per team per season: {per_team_season:.2f}")
        by_period = costs.groupby("period")["cost_wp"].agg(["mean", "count"])
        print("by period of first trouble:")
        print((by_period.assign(mean=by_period["mean"] * 100)).round(2).to_string())

    costs.to_csv(HAZARD_DIR.parent / "policy_costs.csv", index=False)


if __name__ == "__main__":
    run()
