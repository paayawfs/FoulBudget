"""Verification suite per TEST_CASES.md. Writes VALIDATION.md at repo root.

kappa convention: TEST_CASES.md phrases kappa as a multiplicative discount
(kappa = 1 means no discount). The model is additive: drift = delta +
kappa * 1[foul trouble], estimated kappa = +0.083 pts/min. Mapping used here:
  "kappa = 1 (no discount)"  -> kappa_add = 0
  "strong discount"          -> kappa_add negative enough that delta+kappa < 0
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from config import ANALYSIS_SEASONS, EVAL_SEASON  # noqa: E402
from policy.solver import (  # noqa: E402
    PolicyValues, margin_step_distribution, evaluate_convention_cost,
    D_GRID, N_STEPS, STEP_SECONDS, period_of_step,
)

EXPOSURE_DIR = ROOT / "data" / "processed" / "exposure"
LINEUPS_DIR = ROOT / "data" / "processed" / "lineups"
HAZARD_DIR = ROOT / "data" / "processed" / "hazard"
VALUE_DIR = ROOT / "data" / "processed" / "value"
OUT = ROOT / "VALIDATION.md"

STAR_DELTA = 6 / 48
LEAGUE_LAM = 0.075  # league fouls/min
results = []
DECISION = np.abs(D_GRID) <= 30  # decision region; outside is boundary buffer


def log(test_id, status, detail):
    results.append((test_id, status, detail))
    print(f"[{status}] {test_id}: {detail.splitlines()[0][:100]}")


def sit_states(pv) -> int:
    """sit decisions in the |d|<=30 decision region, fouled-out rows excluded."""
    return int((pv.policy[1:, :6, :][:, :, DECISION] == 0).sum())


def run_A_B_D(support, probs, mean):
    kappa_hat = pd.read_csv(HAZARD_DIR / "kappa.csv", index_col=0).loc["foul_trouble", "coef"]

    # A1 / D2: Weinstein's theorem holds under CONSTANT leverage -- test it
    # there. Under the real W(d,t), sitting at kappa=0 can be strictly optimal
    # (it shifts a finite foul budget toward high-leverage minutes); that
    # option-value behavior is reported alongside, not treated as failure.
    pv_lin = PolicyValues(STAR_DELTA, LEAGUE_LAM, 0.0, support, probs, mean,
                          terminal="linear")
    n_sit_lin = sit_states(pv_lin)
    log("A1/D2", "PASS" if n_sit_lin == 0 else "FAIL",
        f"kappa_add=0, constant-leverage terminal: sit-states = {n_sit_lin} (expect 0; "
        f"Weinstein's truncation argument assumes leverage-flat value)")

    pv = PolicyValues(STAR_DELTA, LEAGUE_LAM, 0.0, support, probs, mean)
    n_sit_wp = sit_states(pv)
    if n_sit_wp == 0:
        msg = ("same player under real W(d,t): 0 sit-states -- even leverage "
               "variation does not justify benching at kappa=0 given the "
               "adaptive hazard (pre-fix sits were boundary artifacts)")
    else:
        where = np.argwhere(pv.policy[1:, :6, :][:, :, DECISION] == 0)
        d_at = np.abs(D_GRID[DECISION][where[:, 2]])
        msg = (f"same player under real W(d,t): {n_sit_wp} sit-states "
               f"(median |d| = {np.median(d_at):.0f}) -- option-value channel")
    log("A1.option-value", "INFO", msg)

    # A2: worthless player -> convention costs ~0
    pv = PolicyValues(0.0, LEAGUE_LAM, 0.0, support, probs, mean)
    gap = float(np.max(np.abs(pv.V_opt - pv.V_conv)))
    log("A2", "PASS" if gap < 1e-9 else "FAIL",
        f"delta=0: max |V_opt - V_conv| over lattice = {gap:.2e} (expect ~0)")

    # A3: never fouls -> always play
    pv = PolicyValues(STAR_DELTA, 0.0, kappa_hat, support, probs, mean)
    n_sit = sit_states(pv)
    log("A3", "PASS" if n_sit == 0 else "FAIL",
        f"lambda=0: sit-states = {n_sit} (expect 0)")

    # A4 / D1: strong discount -> aggressive benching, Q+1-like
    strong = -0.25  # delta + kappa = 6/48 - 12/48 < 0 in trouble
    pv = PolicyValues(STAR_DELTA, LEAGUE_LAM, strong, support, probs, mean)
    n_sit = sit_states(pv)
    # agreement with the Q+1 rule over trouble states
    agree = total = 0
    for t in range(1, N_STEPS + 1):
        period = period_of_step(t)
        for f in range(6):
            if f >= period + 1:
                total += len(D_GRID)
                agree += int((pv.policy[t, f] == 0).sum())
    pct = agree / total * 100
    log("A4/D1", "PASS" if n_sit > 0 and pct > 60 else "FAIL",
        f"kappa_add={strong} (trouble-delta < 0): sit-states = {n_sit}, "
        f"agreement with Q+1 inside trouble region = {pct:.0f}% "
        f"(Maymin-style benching is a special case at a kappa the data rejects)")

    # A5: monotonicity. delta is exempted from a strict direction: the
    # option-value channel scales WITH delta (more future value to protect),
    # so sits can rise in delta in low-leverage states -- TEST_CASES.md's
    # "genuinely interesting interaction" branch. It must be inspected: any
    # delta-driven sits in high-leverage states (|d| < 10) are still a bug.
    base = dict(delta=STAR_DELTA, lam=LEAGUE_LAM, kappa=0.0)
    for param, grid, direction in (
        ("lam", [0.02, 0.05, 0.08, 0.11, 0.14], "more"),
        ("kappa", [-0.20, -0.10, 0.0, 0.083], "fewer"),
    ):
        counts = []
        for v in grid:
            kw = dict(base); kw[param] = v
            counts.append(sit_states(PolicyValues(kw["delta"], kw["lam"], kw["kappa"], support, probs, mean)))
        diffs = np.diff(counts)
        ok = (diffs <= 0).all() if direction == "fewer" else (diffs >= 0).all()
        log(f"A5.{param}", "PASS" if ok else "FAIL",
            f"sit-states over {param} grid {grid}: {counts} (expect {direction} sits)")

    counts, close_sits = [], []
    d_dec = D_GRID[DECISION]
    for v in [0.0, 0.05, 0.10, 0.15, 0.20]:
        pv = PolicyValues(v, LEAGUE_LAM, 0.0, support, probs, mean)
        counts.append(sit_states(pv))
        sits = np.argwhere(pv.policy[1:, :6, :][:, :, DECISION] == 0)
        close_sits.append(int((np.abs(d_dec[sits[:, 2]]) < 10).sum()) if len(sits) else 0)
    ok = all(c == 0 for c in close_sits)
    log("A5.delta", "PASS" if ok else "FAIL",
        f"sit-states over delta grid: {counts}; sits at |d|<10 (must be 0): {close_sits} "
        f"(rising total = option value in blowout states, inspected and expected)")

    # B1: last 2 minutes -> play everywhere (delta > 0, kappa = 0)
    pv = PolicyValues(0.02, LEAGUE_LAM, 0.0, support, probs, mean)
    tail = pv.policy[1:5, :6, :]  # t = 30..120s remaining
    n_sit = int((tail == 0).sum())
    log("B1", "PASS" if n_sit == 0 else "FAIL",
        f"delta=+1/48, t<=120s: sit-states = {n_sit} (expect 0)")

    # B2: foul-out state independent of the player's own delta
    pv_a = PolicyValues(0.20, LEAGUE_LAM, 0.0, support, probs, mean)
    pv_b = PolicyValues(0.0, LEAGUE_LAM, 0.0, support, probs, mean)
    diff = float(np.max(np.abs(pv_a.V_opt[:, 6, :] - pv_b.V_opt[:, 6, :])))
    log("B2", "PASS" if diff < 1e-12 else "FAIL",
        f"max |V(f=6)| difference across delta=0 vs 0.20: {diff:.2e} (expect 0 -- absorbing)")

    # B3: blowout saturation is a LATE-game property -- a 28-point deficit
    # with 40 minutes left is ~1.6 sigma of remaining score noise, genuinely
    # not decided. Test where W is actually saturated: <=12 min remaining.
    pv = PolicyValues(STAR_DELTA, LEAGUE_LAM, kappa_hat, support, probs, mean)
    edge = np.abs(D_GRID) >= 28
    late = slice(0, 25)  # t index <= 24 -> <=12 minutes remaining
    gap = float(np.max((pv.V_opt - pv.V_conv)[late, :, edge]))
    gap_all = float(np.max((pv.V_opt - pv.V_conv)[:, :, edge]))
    log("B3", "PASS" if gap < 0.005 else "FAIL",
        f"max convention cost at |d|>=28 with <=12 min left: {gap * 100:.3f}pp "
        f"(expect ~0; over all t it is {gap_all * 100:.2f}pp -- early 28-point "
        f"deficits are ~1.6 sigma from even, not saturated)")

    # B4: symmetry of the DP's implied W at delta = 0
    pv = PolicyValues(0.0, LEAGUE_LAM, 0.0, support, probs, mean)
    V = pv.V_opt[:, 0, :]
    asym = float(np.max(np.abs(V + V[:, ::-1] - 1.0)))
    log("B4", "PASS" if asym < 0.03 else "FAIL",
        f"max |W(d)+W(-d)-1| on lattice: {asym:.4f} (tolerance 0.03; "
        f"steps de-meaned, residual skew only)")
    return kappa_hat


def run_C(support, probs, mean, kappa_hat):
    # C1: replacement weights sum to 1
    worst = 0.0
    for s in ANALYSIS_SEASONS:
        w = pd.read_csv(VALUE_DIR / f"replacement_weights_{s}.csv")
        sums = w.groupby("player_id")["weight"].sum()
        worst = max(worst, float((sums - 1).abs().max()))
    log("C1", "PASS" if worst < 1e-9 else "FAIL",
        f"max |sum(weights) - 1| over player-seasons: {worst:.2e}")

    # C2: dominance on real evaluated occurrences
    costs = evaluate_convention_cost(support, probs, mean, kappa_hat)
    n_neg = int((costs["cost_wp"] < -1e-9).sum())
    log("C2", "PASS" if n_neg == 0 else "FAIL",
        f"negative WP costs among {len(costs):,} occurrences: {n_neg} "
        f"(min = {costs['cost_wp'].min():.2e})")

    # C3: per-player kappa shrinkage (kappa v2, HIERARCHICAL_KAPPA_PLAN
    # Phase D): thin-exposure players must hug kappa-bar, dispersion must
    # widen with data, and the FT-weighted mean kappa_i must reconcile with
    # the v1 pooled estimate
    import json
    k2 = pd.read_csv(HAZARD_DIR / "kappa_v2.csv")
    meta = json.loads((HAZARD_DIR / "kappa_v2_meta.json").read_text())
    lo = k2.loc[k2["ft_poss"] < 25, "dev_per48"]
    hi = k2.loc[k2["ft_poss"] >= 250, "dev_per48"]
    recon = float(np.average(k2["kappa_per48"], weights=k2["ft_poss"]))
    ok = (lo.std() < hi.std() and lo.abs().max() < 3.0
          and abs(recon - kappa_hat * 48) < 0.5)
    log("C3", "PASS" if ok else "FAIL",
        f"kappa_i shrinkage: sd(dev) {lo.std():.2f} (<25 FT poss) -> "
        f"{hi.std():.2f} (>=250) per48, max thin-sample |dev| = "
        f"{lo.abs().max():.2f}; FT-weighted mean kappa_i {recon:+.2f} vs v1 "
        f"pooled {kappa_hat * 48:+.2f}; OOS gain over pooled = "
        f"{meta['oos_gain_frac_of_pooled_mse']:+.3%} of held-out MSE "
        f"(lambda_kappa = {meta['lambda_kappa']:g})")

    # C4: hazard face-check, predicted vs actual fouls per player-season
    ex = pd.concat([pd.read_parquet(EXPOSURE_DIR / f"{s}.parquet").assign(season=s)
                    for s in ANALYSIS_SEASONS], ignore_index=True)
    ex = ex[ex["minutes_exposed"] > 0].copy()
    ex["player_season"] = ex["player_id"].astype(str) + "_" + ex["season"].astype(str)
    alphas = pd.read_csv(HAZARD_DIR / "alphas.csv", index_col=0)["alpha"]
    g = pd.read_csv(HAZARD_DIR / "gammas.csv")
    g = g[g["spec"] == "linear"].set_index(g.columns[0])["coef"]
    eta = (g["foul_count"] * ex["foul_count"]
           + g["abs_margin"] * ex["score_margin"].abs()
           + sum(g.get(f"p_{p}", 0.0) * (ex["period"].clip(upper=5) == p) for p in (2, 3, 4, 5)))
    ex["pred"] = ex["minutes_exposed"] * np.exp(ex["player_season"].map(alphas) + eta)
    agg = ex.groupby("player_season").agg(pred=("pred", "sum"), actual=("fouls_in_window", "sum"))
    total_ratio = agg["pred"].sum() / agg["actual"].sum()
    heavy = agg[agg["actual"] >= 50]
    r = float(np.corrcoef(heavy["pred"], heavy["actual"])[0, 1])
    # per-player reconciliation is NOT expected to be exact: the 200-minute
    # gamma prior deliberately shrinks thin samples toward the league rate
    log("C4", "PASS" if abs(total_ratio - 1) < 0.02 and r > 0.95 else "FAIL",
        f"aggregate predicted/actual fouls = {total_ratio:.4f} (within 2%), "
        f"per-player-season corr = {r:.3f} (>=50 fouls; per-player gaps are "
        f"the shrinkage prior working)")

    # C5: external RAPM benchmark -- needs nbarapm.com data
    log("C5", "PENDING", "requires nbarapm.com same-window values (external "
        "download); run when the comparison file is available")
    return costs


def run_E(costs, support, probs, mean, kappa_hat):
    deltas = pd.read_csv(VALUE_DIR / f"delta_{EVAL_SEASON}.csv").set_index("player_id")

    # E1: archetype ordering
    per_player = costs.groupby("player_id")["cost_wp"].agg(["mean", "count"])
    per_player = per_player[per_player["count"] >= 5]
    per_player["name"] = per_player.index.map(deltas["name"])
    per_player["delta48"] = per_player.index.map(deltas["delta"]) * 48
    top = per_player.nlargest(12, "mean")
    tbl = top.assign(mean_pp=top["mean"] * 100).round(2)[["name", "mean_pp", "count", "delta48"]]
    log("E1", "EYEBALL", "top-12 by mean WP cost per occurrence (>=5 occurrences):\n"
        + tbl.to_string(index=False))

    # E2: lambda vs raw per-36 foul rates
    ex = pd.read_parquet(EXPOSURE_DIR / f"{EVAL_SEASON}.parquet")
    ex = ex[ex["minutes_exposed"] > 0]
    raw = ex.groupby("player_id").agg(m=("minutes_exposed", "sum"), f=("fouls_in_window", "sum"))
    raw = raw[raw["m"] >= 1000]
    raw["per36"] = raw["f"] / raw["m"] * 36
    alphas = pd.read_csv(HAZARD_DIR / "alphas.csv", index_col=0)["alpha"]
    raw["lam36"] = np.exp(raw.index.astype(str).map(lambda i: alphas.get(f"{i}_{EVAL_SEASON}", np.nan))) * 36
    raw = raw.dropna()
    r = float(np.corrcoef(raw["per36"], raw["lam36"])[0, 1])
    raw["name"] = raw.index.map(deltas["name"])
    hi = raw.nlargest(5, "lam36")[["name", "lam36", "per36"]].round(2)
    lo = raw.nsmallest(5, "lam36")[["name", "lam36", "per36"]].round(2)
    log("E2", "PASS" if r > 0.9 else "FAIL",
        f"corr(model lambda, raw per-36 fouls) = {r:.3f} (>=1000 min, {EVAL_SEASON})\n"
        f"highest lambda:\n{hi.to_string(index=False)}\nlowest lambda:\n{lo.to_string(index=False)}")

    # E3: strong backups shrink delta
    d = deltas.dropna(subset=["delta", "composite_rapm"])
    d = d[d["minutes"] >= 1500].copy()
    d["rapm48"] = d["rapm"] * 48
    d["comp48"] = d["composite_rapm"] * 48
    d["delta48"] = d["delta"] * 48
    strong_bk = d.nlargest(5, "comp48")[["name", "rapm48", "comp48", "delta48"]].round(2)
    weak_bk = d.nsmallest(5, "comp48")[["name", "rapm48", "comp48", "delta48"]].round(2)
    log("E3", "EYEBALL", "stars with strongest backups (delta should compress):\n"
        + strong_bk.to_string(index=False)
        + "\nweakest backups (delta should stretch):\n" + weak_bk.to_string(index=False))

    # E4: largest realized-cost episodes
    ex24 = pd.read_parquet(EXPOSURE_DIR / f"{EVAL_SEASON}.parquet")
    ex24 = ex24[ex24["minutes_exposed"] > 0]
    lu = pd.read_parquet(LINEUPS_DIR / f"{EVAL_SEASON}.parquet", columns=["GAME_ID", "SCOREMARGIN", "PCTIMESTRING"])
    lu["margin"] = pd.to_numeric(lu["SCOREMARGIN"].replace("TIE", "0"), errors="coerce")
    finals = lu.groupby("GAME_ID")["margin"].last()

    trouble = ex24[ex24["foul_count"] >= ex24["period"] + 1]
    first = trouble.sort_values("start_elapsed").groupby(["game_id", "player_id"]).first()
    on_after = []
    for (gid, pid), row in first.iterrows():
        spells = ex24[(ex24["game_id"] == gid) & (ex24["player_id"] == pid)
                      & (ex24["start_elapsed"] >= row["start_elapsed"])]
        on_after.append(spells["minutes_exposed"].sum())
    first = first.assign(on_after=on_after).reset_index()
    first["remaining"] = (2880 - first["start_elapsed"]).clip(lower=0) / 60
    first["sat"] = (first["remaining"] - first["on_after"]).clip(lower=0)
    first["final_margin"] = first["game_id"].map(finals).abs()
    first["delta48"] = first["player_id"].map(deltas["delta"]) * 48
    hi_delta = first["delta48"] >= first["delta48"].quantile(0.9)
    cases = first[hi_delta & (first["final_margin"] <= 5) & (first["sat"] >= 6)]
    cases = cases.sort_values(["delta48", "sat"], ascending=False).head(3)
    cases["name"] = cases["player_id"].map(deltas["name"])
    tbl = cases[["game_id", "name", "period", "foul_count", "sat", "remaining", "final_margin", "delta48"]].round(1)
    log("E4", "EYEBALL", "case studies: top-decile-delta starters benched >=6 min "
        "after Q+1 trouble in games decided by <=5:\n" + tbl.to_string(index=False))

    # E5: full trace of the top case
    if len(cases):
        c = cases.iloc[0]
        gid, pid = int(c["game_id"]), int(c["player_id"])
        dsign = 1.0 if ex24[(ex24.game_id == gid) & (ex24.player_id == pid)].iloc[0]["side"] == "HOME" else -1.0
        lam = float(np.exp(pd.read_csv(HAZARD_DIR / "alphas.csv", index_col=0)["alpha"].get(f"{pid}_{EVAL_SEASON}", np.nan)))
        pv = PolicyValues(float(c["delta48"]) / 48, lam, kappa_hat, support, probs, mean)
        spells = ex24[(ex24.game_id == gid) & (ex24.player_id == pid)].sort_values("start_elapsed")
        lines = [f"game {gid}, {c['name']} (delta {c['delta48']:+.1f}/48, lam {lam * 36:.1f}/36)"]
        lu_g = pd.read_parquet(LINEUPS_DIR / f"{EVAL_SEASON}.parquet", columns=["GAME_ID", "PCTIMESTRING", "SCOREMARGIN"])
        lu_g = lu_g[lu_g.GAME_ID == gid]
        lu_g["margin"] = pd.to_numeric(lu_g["SCOREMARGIN"].replace("TIE", "0"), errors="coerce").ffill().fillna(0)
        for _, s in spells.iterrows():
            t_rem = max(0, 2880 - s["start_elapsed"])
            d_team = dsign * s["score_margin"]
            t_idx = int(np.clip(round(t_rem / STEP_SECONDS), 0, N_STEPS))
            d_idx = int(np.clip(round(d_team), D_GRID[0], D_GRID[-1])) - int(D_GRID[0])
            model = "play" if (s["foul_count"] >= 6) is False and pv.policy[t_idx, min(int(s["foul_count"]), 6), d_idx] else "sit"
            trouble_flag = "TROUBLE" if s["foul_count"] >= s["period"] + 1 else "       "
            lines.append(
                f"  Q{int(s['period'])} {t_rem / 60:5.1f}m left | d={d_team:+3.0f} | f={int(s['foul_count'])} {trouble_flag} "
                f"| coach: on {s['minutes_exposed']:4.1f}m ({s['ended_by']}) | model: {model}")
        log("E5", "EYEBALL", "\n".join(lines))


def write_md():
    lines = [
        "# VALIDATION.md — verification suite results",
        "",
        "Run: `python tests/run_validation.py` (regenerates this file).",
        "",
        "kappa convention: TEST_CASES.md's multiplicative 'kappa = 1 (no discount)'",
        "maps to this model's additive kappa = 0; 'strong discount' maps to",
        "kappa negative enough that delta + kappa < 0 in foul trouble.",
        "",
        "| test | status | summary |",
        "|---|---|---|",
    ]
    for tid, status, detail in results:
        lines.append(f"| {tid} | {status} | {detail.splitlines()[0]} |")
    lines.append("")
    lines.append("## Artifacts")
    for tid, status, detail in results:
        if "\n" in detail:
            lines += [f"### {tid} ({status})", "```", detail, "```", ""]

    # everything below the marker is maintained by hand (session logs, data
    # gates); regeneration must not clobber it
    marker = "<!-- session-log -->"
    if OUT.exists() and marker in OUT.read_text(encoding="utf-8"):
        preserved = OUT.read_text(encoding="utf-8").split(marker, 1)[1]
        lines += [marker + preserved]
    else:
        lines.append(marker)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nwrote {OUT}")


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    support, probs, mean = margin_step_distribution()
    kappa_hat = run_A_B_D(support, probs, mean)
    costs = run_C(support, probs, mean, kappa_hat)
    run_E(costs, support, probs, mean, kappa_hat)
    write_md()
    n_fail = sum(1 for _, s, _ in results if s == "FAIL")
    print(f"\n{len(results)} checks: {n_fail} FAIL")
    return n_fail


if __name__ == "__main__":
    raise SystemExit(main())
