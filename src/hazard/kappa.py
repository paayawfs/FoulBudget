"""Playing-scared discount kappa per REFERENCE.md Section 3.4.

    net_rating_it = theta_i + kappa * 1[foul_trouble_it] + controls + eps

Unit of observation: one exposure spell (fixed player, fixed foul count).
Outcome: team net points per minute while the player is on court, signed to
the player's side. Minutes-weighted least squares with player-season and
opponent-season fixed effects absorbed as sparse dummies, plus period dummies,
|margin|, and a home indicator.

kappa is reported as an upper bound on the causal effect (foul trouble is not
randomly assigned; opponent controls absorb the matchup channel we can see).
Sign convention: negative kappa = the player's lineups do worse while he
carries foul trouble.

ponytail: naive (non-clustered) SEs printed with a game-cluster note; move to
game-clustered SEs when the number goes in the paper.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import sparse

EXPOSURE_DIR = Path(__file__).resolve().parents[2] / "data" / "processed" / "exposure"
OUT_DIR = Path(__file__).resolve().parents[2] / "data" / "processed" / "hazard"
import sys as _sys
_sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import ANALYSIS_SEASONS as SEASONS, foul_trouble_threshold


def load() -> pd.DataFrame:
    df = pd.concat(
        [pd.read_parquet(EXPOSURE_DIR / f"{s}.parquet").assign(season=s) for s in SEASONS],
        ignore_index=True,
    )
    df = df[df["minutes_exposed"] > 0].copy()
    sign = np.where(df["side"] == "HOME", 1.0, -1.0)
    df["net_per_min"] = sign * df["margin_change"] / df["minutes_exposed"]
    df["foul_trouble"] = (df["foul_count"] >= foul_trouble_threshold(df["period"])).astype(float)
    df["abs_margin"] = df["score_margin"].abs()
    df["home"] = (df["side"] == "HOME").astype(float)
    df["player_season"] = df["player_id"].astype(str) + "_" + df["season"].astype(str)
    df["opp_season"] = df["opponent"].astype(str) + "_" + df["season"].astype(str)
    # spell opens right after the player's own foul -> the opposing free
    # throws from that foul land inside this spell's margin_change, which
    # mechanically depresses measured performance at higher foul counts
    prev = df.groupby(["game_id", "player_id"], sort=False).shift()
    df["after_own_foul"] = (
        (prev["ended_by"] == "foul") & (prev["period"] == df["period"])
    ).fillna(False)
    return df


def fit(df: pd.DataFrame, tier: pd.Series = None, extra_covs: pd.DataFrame = None):
    """tier: optional per-row group label; expands the foul_trouble column
    into one column per tier (used by the Phase A grouping audit).
    extra_covs: optional additional covariate columns (used by the B0
    selection check's window main effect)."""
    if tier is not None:
        covs = pd.DataFrame({
            f"foul_trouble[{v}]": df["foul_trouble"] * (tier == v).astype(float)
            for v in sorted(tier.dropna().unique())
        })
        covs["abs_margin"] = df["abs_margin"]
        covs["home"] = df["home"]
    else:
        covs = pd.DataFrame({
            "foul_trouble": df["foul_trouble"],
            "abs_margin": df["abs_margin"],
            "home": df["home"],
        })
    if extra_covs is not None:
        for c in extra_covs.columns:
            covs[c] = extra_covs[c].to_numpy()
    for p in (2, 3, 4, 5):
        covs[f"p_{p}"] = (df["period"].clip(upper=5) == p).astype(float)

    ps = pd.Categorical(df["player_season"])
    os_ = pd.Categorical(df["opp_season"])
    n = len(df)
    D_ps = sparse.csr_matrix(
        (np.ones(n), (np.arange(n), ps.codes)), shape=(n, len(ps.categories))
    )
    # drop one opponent-season dummy for identification vs the player FE block
    D_os = sparse.csr_matrix(
        (np.ones(n), (np.arange(n), os_.codes)), shape=(n, len(os_.categories))
    )[:, 1:]
    X = sparse.hstack([sparse.csr_matrix(covs.to_numpy()), D_ps, D_os]).tocsr()

    y = df["net_per_min"].to_numpy()
    w = df["minutes_exposed"].to_numpy()

    Xw = X.multiply(w[:, None]).tocsr()
    A = (X.T @ Xw).toarray()
    A[np.diag_indices_from(A)] += 1e-8  # numerical guard
    b = X.T @ (w * y)
    beta = np.linalg.solve(A, b)

    k = covs.shape[1]
    resid = y - X @ beta
    dof = n - np.linalg.matrix_rank(A)
    sigma2 = float((w * resid**2).sum() / dof)
    cov_beta = sigma2 * np.linalg.inv(A)
    se = np.sqrt(np.diag(cov_beta)[:k])
    return pd.DataFrame({"coef": beta[:k], "se": se}, index=covs.columns)


def run() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    df = load()
    ft_min = df.loc[df["foul_trouble"] == 1, "minutes_exposed"].sum()
    print(f"spells: {len(df):,} | foul-trouble spells: {int(df['foul_trouble'].sum()):,} "
          f"({ft_min:,.0f} foul-trouble minutes)")

    res = fit(df)
    res["per48"] = res["coef"] * 48
    res["t"] = res["coef"] / res["se"]
    print("\nkappa regression (net points per minute, minutes-weighted, "
          "player-season + opponent-season FE):")
    print(res.round(4).to_string())

    kappa = res.loc["foul_trouble"]
    print(f"\nKAPPA: {kappa['coef']:+.4f} pts/min ({kappa['per48']:+.2f} per 48), "
          f"t = {kappa['t']:.2f}  [naive SEs; cluster by game before publishing]")

    # sensitivity: drop spells opening right after the player's own foul, so
    # the ensuing opposing FTs can't be booked against the new (higher) count
    sens = fit(df[~df["after_own_foul"]])
    ks = sens.loc["foul_trouble"]
    print(f"kappa excluding after-own-foul spells "
          f"({df['after_own_foul'].mean():.0%} of spells dropped): "
          f"{ks['coef']:+.4f} pts/min ({ks['coef'] * 48:+.2f} per 48), "
          f"t = {ks['coef'] / ks['se']:.2f}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    res.to_csv(OUT_DIR / "kappa.csv")


if __name__ == "__main__":
    run()
