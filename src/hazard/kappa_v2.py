"""Per-player playing-scared deviations — HIERARCHICAL_KAPPA_PLAN Phase B/D.

Extends the kappa spell WLS (kappa.py): same outcome, weights, player-season
and opponent-season FE, and state controls, plus one deviation column per
player with any foul-trouble exposure: foul_trouble x 1[player i]. The global
foul_trouble column stays lightly penalized (kappa-bar); deviation columns
are ridge-penalized toward 0 = partial pooling toward the league mean
(Phase A on the 5-season window chose league-wide grouping, no tier layer).

lambda_kappa by 2-fold CV over games, scored as minutes-weighted MSE on
held-out FOUL-TROUBLE spells only (the columns being tuned are zero
elsewhere). A pooled reference (deviations forced to ~0 via lambda=1e12)
gives the Phase D out-of-sample gate: does kappa_i beat kappa-bar held out?

kappa_i = kappa-bar + dev_i, reported per 48. Writes
data/processed/hazard/kappa_v2.csv and reports/kappa_v2.md.

ponytail: teammate quality not controlled (the RAPM-interaction route would
be); player-season FE limit the bias to trouble-correlated lineup shifts.
Upgrade path: foul-trouble columns inside the RAPM stint design.
ponytail: no per-player SEs — the OOS gate arbitrates heterogeneity; add a
covariance solve if Phase E needs interval language.
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import sparse

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import ANALYSIS_SEASONS  # noqa: E402
from hazard.kappa import load  # noqa: E402

HAZARD_DIR = Path(__file__).resolve().parents[2] / "data" / "processed" / "hazard"
OUT_MD = Path(__file__).resolve().parents[2] / "reports" / "kappa_v2.md"
POSS_PER_MIN = 100 / 48
REPORT_THRESHOLD = 250          # pooled FT possessions, per Phase A decision
GUARD = 1e-8                    # numerical guard = "lightly penalized"
POOLED_LAMBDA = 1e12            # deviations effectively off -> pooled model
LAMBDA_GRID = (10.0, 40.0, 160.0, 640.0, 2560.0, 10240.0)


def build_design(df: pd.DataFrame):
    """X = [dense controls | per-player FT deviations | player-season FE |
    opp-season FE], plus the penalty template (1.0 where lambda applies)."""
    covs = pd.DataFrame({
        "foul_trouble": df["foul_trouble"],
        "abs_margin": df["abs_margin"],
        "home": df["home"],
    })
    for p in (2, 3, 4, 5):
        covs[f"p_{p}"] = (df["period"].clip(upper=5) == p).astype(float)

    ft_players = np.sort(df.loc[df["foul_trouble"] == 1, "player_id"].unique())
    pcode = pd.Categorical(df["player_id"], categories=ft_players).codes
    n = len(df)
    mask = (df["foul_trouble"].to_numpy() == 1) & (pcode >= 0)
    D_dev = sparse.csr_matrix(
        (np.ones(mask.sum()), (np.flatnonzero(mask), pcode[mask])),
        shape=(n, len(ft_players)),
    )

    ps = pd.Categorical(df["player_season"])
    os_ = pd.Categorical(df["opp_season"])
    D_ps = sparse.csr_matrix(
        (np.ones(n), (np.arange(n), ps.codes)), shape=(n, len(ps.categories))
    )
    D_os = sparse.csr_matrix(
        (np.ones(n), (np.arange(n), os_.codes)), shape=(n, len(os_.categories))
    )[:, 1:]

    X = sparse.hstack([sparse.csr_matrix(covs.to_numpy()), D_dev, D_ps, D_os]).tocsr()
    k = covs.shape[1]
    is_dev = np.zeros(X.shape[1])
    is_dev[k:k + len(ft_players)] = 1.0
    return X, ft_players, k, is_dev


def solve(A_base: np.ndarray, b: np.ndarray, is_dev: np.ndarray, lam: float):
    A = A_base.copy()
    A[np.diag_indices_from(A)] += GUARD + is_dev * lam
    return np.linalg.solve(A, b)


def run() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    df = load()
    X, ft_players, k, is_dev = build_design(df)
    y = df["net_per_min"].to_numpy()
    w = df["minutes_exposed"].to_numpy()
    ft_mask = df["foul_trouble"].to_numpy() == 1
    print(f"spells: {len(df):,} | deviation columns: {len(ft_players)} | "
          f"design: {X.shape[1]} cols")

    # ---- CV over lambda: 2 game-parity folds, scored on held-out FT spells
    fold = (df["game_id"].to_numpy() % 2).astype(bool)
    cv = {}
    for lam in LAMBDA_GRID + (POOLED_LAMBDA,):
        cv[lam] = 0.0
    for train in (fold, ~fold):
        Xt = X[train]
        A_base = (Xt.T @ Xt.multiply(w[train][:, None])).toarray()
        b = Xt.T @ (w[train] * y[train])
        ho = ~train & ft_mask
        Xh, yh, wh = X[ho], y[ho], w[ho]
        for lam in cv:
            beta = solve(A_base, b, is_dev, lam)
            resid = yh - Xh @ beta
            cv[lam] += float((wh * resid**2).sum() / wh.sum())

    pooled_mse = cv.pop(POOLED_LAMBDA)
    best_lam = min(cv, key=cv.get)
    if best_lam in (LAMBDA_GRID[0], LAMBDA_GRID[-1]):
        print(f"WARNING: best lambda {best_lam:g} is at the grid edge — extend the grid")
    print("\nCV (held-out FT-spell weighted MSE):")
    for lam, mse in cv.items():
        tag = " <- chosen" if lam == best_lam else ""
        print(f"  lambda {lam:>8g}: {mse:.6f}{tag}")
    print(f"  pooled (no deviations): {pooled_mse:.6f}")
    oos_gain = pooled_mse - cv[best_lam]
    print(f"OOS gate: pooled - best = {oos_gain:+.6f} "
          f"({oos_gain / pooled_mse:+.3%} of pooled MSE)")

    # ---- final fit on all data at chosen lambda
    A_base = (X.T @ X.multiply(w[:, None])).toarray()
    b = X.T @ (w * y)
    beta = solve(A_base, b, is_dev, best_lam)
    kappa_bar = beta[0]
    dev = beta[k:k + len(ft_players)]

    ftd = df[ft_mask]
    ft_min = ftd.groupby("player_id")["minutes_exposed"].sum().reindex(ft_players)
    out = pd.DataFrame({
        "player_id": ft_players,
        "ft_poss": (ft_min * POSS_PER_MIN).round(1).to_numpy(),
        "dev_per48": dev * 48,
        "kappa_per48": (kappa_bar + dev) * 48,
    })
    out["reportable"] = out["ft_poss"] >= REPORT_THRESHOLD
    lineups_dir = Path(__file__).resolve().parents[2] / "data" / "processed" / "lineups"
    names = pd.concat([
        pd.read_parquet(lineups_dir / f"{s}.parquet",
                        columns=[f"PLAYER{i}_ID", f"PLAYER{i}_NAME"])
        .rename(columns={f"PLAYER{i}_ID": "player_id", f"PLAYER{i}_NAME": "name"})
        for s in ANALYSIS_SEASONS for i in (1, 2, 3)
    ]).dropna().drop_duplicates("player_id", keep="last").set_index("player_id")["name"]
    out.insert(1, "name", out["player_id"].map(names))
    HAZARD_DIR.mkdir(parents=True, exist_ok=True)
    out.to_csv(HAZARD_DIR / "kappa_v2.csv", index=False)
    (HAZARD_DIR / "kappa_v2_meta.json").write_text(json.dumps({
        "kappa_bar_per48": kappa_bar * 48,
        "lambda_kappa": best_lam,
        "oos_gain_frac_of_pooled_mse": oos_gain / pooled_mse,
    }, indent=1))

    # ---- report
    lines = [f"# kappa v2 — per-player deviations, ridge partial pooling "
             f"({len(ANALYSIS_SEASONS)} seasons: {ANALYSIS_SEASONS[0]}–{ANALYSIS_SEASONS[-1]})", ""]
    lines.append(f"deviation columns: {len(ft_players)} players | "
                 f"lambda_kappa = {best_lam:g} (2-fold CV over games)")
    lines.append(f"kappa-bar (global): {kappa_bar * 48:+.2f} per 48")
    v1 = pd.read_csv(HAZARD_DIR / "kappa.csv", index_col=0).loc["foul_trouble", "coef"]
    lines.append(f"reconciliation: v1 pooled kappa {v1 * 48:+.2f} per 48; "
                 f"FT-minutes-weighted mean kappa_i "
                 f"{np.average(out['kappa_per48'], weights=ft_min):+.2f} per 48")
    lines.append("")
    lines.append("## OOS gate (held-out FT spells, minutes-weighted MSE)")
    lines.append(f"pooled kappa-bar: {pooled_mse:.6f} | with kappa_i: {cv[best_lam]:.6f} "
                 f"| gain {oos_gain:+.6f} ({oos_gain / pooled_mse:+.3%})")
    lines.append("")
    lines.append("## C3 — shrinkage vs exposure (dev_per48 by pooled FT possessions)")
    bins = pd.cut(out["ft_poss"], [0, 25, 50, 100, 250, 500, np.inf], right=False)
    c3 = out.groupby(bins, observed=True)["dev_per48"].agg(
        n="count", sd="std", max_abs=lambda s: s.abs().max())
    lines.append(c3.round(2).to_string())
    lines.append("")
    rep = out[out["reportable"]].sort_values("kappa_per48")
    lines.append(f"## face validity — reportable players (>= {REPORT_THRESHOLD} FT poss, "
                 f"n = {len(rep)})")
    lines.append("most negative kappa_i (per 48):")
    lines.append(rep.head(5)[["name", "ft_poss", "kappa_per48"]].round(2).to_string(index=False))
    lines.append("least negative / most positive:")
    lines.append(rep.tail(5)[["name", "ft_poss", "kappa_per48"]].round(2).to_string(index=False))

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print("\n" + "\n".join(lines))
    print(f"\nwrote {HAZARD_DIR / 'kappa_v2.csv'} and {OUT_MD}")


if __name__ == "__main__":
    run()
