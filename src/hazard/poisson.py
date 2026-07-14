"""Poisson foul-hazard model with exposure offset per REFERENCE.md Section 3.3.

    log E[fouls_iw] = log(minutes_iw) + alpha_i + gamma1 * foulcount_iw
                    + gamma2 * X_iw        (period dummies, |score margin|)

Player-season fixed effects alpha_i are profiled out: given gamma they have a
closed-form update (MAP under a gamma prior worth PRIOR_MINUTES of
league-average fouling, which shrinks thin-sample players), so the GLM only
ever sees the small gamma vector. Alternate the two updates to convergence.

Three specs reported:
  - linear foulcount (the headline gamma1)
  - foul-trouble indicator (fouls >= period + 1), the convention's own trigger
  - foul-count dummies (shape; feeds the foul-out-probability chart later)

Outputs data/processed/hazard/{gammas.csv, alphas.csv}.

ponytail: no opponent-FT-draw / rest / crew controls yet (Section 5 lists
them); add when the killer-chart numbers need defending. SEs are conditional
on the profiled alphas, so slightly optimistic -- fine at n=447k, flag in text.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

EXPOSURE_DIR = Path(__file__).resolve().parents[2] / "data" / "processed" / "exposure"
OUT_DIR = Path(__file__).resolve().parents[2] / "data" / "processed" / "hazard"
SEASONS = (2022, 2023, 2024)
PRIOR_MINUTES = 200.0
MAX_ITER = 25
TOL = 1e-7


def load_exposure() -> pd.DataFrame:
    df = pd.concat(
        [pd.read_parquet(EXPOSURE_DIR / f"{s}.parquet").assign(season=s) for s in SEASONS],
        ignore_index=True,
    )
    dropped = df[df["minutes_exposed"] <= 0]
    print(f"dropping {len(dropped):,} zero-exposure rows "
          f"({dropped['fouls_in_window'].sum():,} fouls, "
          f"{dropped['fouls_in_window'].sum() / df['fouls_in_window'].sum():.1%} of all fouls)")
    df = df[df["minutes_exposed"] > 0].copy()
    df["player_season"] = df["player_id"].astype(str) + "_" + df["season"].astype(str)
    df["foul_trouble"] = (df["foul_count"] >= df["period"] + 1).astype(float)
    df["abs_margin"] = df["score_margin"].abs()
    return df


def covariates(df: pd.DataFrame, foul_term: str) -> pd.DataFrame:
    X = pd.get_dummies(df["period"].clip(upper=5), prefix="p", drop_first=True, dtype=float)
    X["abs_margin"] = df["abs_margin"]
    if foul_term == "linear":
        X.insert(0, "foul_count", df["foul_count"].astype(float))
    elif foul_term == "trouble":
        X.insert(0, "foul_trouble", df["foul_trouble"])
    elif foul_term == "dummies":
        fc = pd.get_dummies(df["foul_count"].clip(upper=5), prefix="fc", drop_first=True, dtype=float)
        X = pd.concat([fc, X], axis=1)
    return X


def fit_profiled(df: pd.DataFrame, foul_term: str):
    """Alternate closed-form alpha updates with a small-gamma Poisson GLM."""
    X = covariates(df, foul_term)
    y = df["fouls_in_window"].to_numpy(dtype=float)
    minutes = df["minutes_exposed"].to_numpy(dtype=float)
    groups = df["player_season"].to_numpy()

    league_rate = y.sum() / minutes.sum()
    fouls_i = pd.Series(y).groupby(groups).sum()
    alpha = pd.Series(0.0, index=fouls_i.index)

    gamma_prev = None
    for it in range(MAX_ITER):
        base = minutes * np.exp(np.zeros(len(df)))
        # alpha update: MAP under gamma prior, exposure adjusted by current gamma
        if gamma_prev is not None:
            eta = X.to_numpy() @ gamma_prev
        else:
            eta = np.zeros(len(df))
        adj_exposure = pd.Series(minutes * np.exp(eta)).groupby(groups).sum()
        alpha = np.log(
            (fouls_i + PRIOR_MINUTES * league_rate) / (adj_exposure + PRIOR_MINUTES)
        )

        offset = np.log(minutes) + pd.Series(groups).map(alpha).to_numpy()
        model = sm.GLM(y, sm.add_constant(X), family=sm.families.Poisson(), offset=offset)
        res = model.fit()
        gamma = res.params.drop("const").to_numpy()

        if gamma_prev is not None and np.max(np.abs(gamma - gamma_prev)) < TOL:
            break
        gamma_prev = gamma

    return res, alpha, it + 1


def report(res, spec: str) -> pd.DataFrame:
    out = pd.DataFrame({
        "coef": res.params,
        "exp": np.exp(res.params),
        "se": res.bse,
    }).drop("const")
    print(f"\n=== spec: {spec} ===")
    print(out.round(4).to_string())
    return out.assign(spec=spec)


def run() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    df = load_exposure()
    print(f"rows: {len(df):,} | fouls: {df['fouls_in_window'].sum():,.0f} | "
          f"player-seasons: {df['player_season'].nunique():,}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tables = []
    for spec in ("linear", "trouble", "dummies"):
        res, alpha, iters = fit_profiled(df, spec)
        print(f"\n[{spec}] converged in {iters} iterations")
        tables.append(report(res, spec))
        if spec == "linear":
            alpha.rename("alpha").to_csv(OUT_DIR / "alphas.csv")

    pd.concat(tables).to_csv(OUT_DIR / "gammas.csv")

    lin = tables[0]
    tr = tables[1]
    print("\nheadline numbers:")
    print(f"  gamma1 (per additional foul): {lin.loc['foul_count', 'coef']:+.4f} "
          f"-> hazard x{lin.loc['foul_count', 'exp']:.3f} per foul carried")
    print(f"  foul-trouble indicator:       {tr.loc['foul_trouble', 'coef']:+.4f} "
          f"-> hazard x{tr.loc['foul_trouble', 'exp']:.3f} when fouls >= Q+1")


if __name__ == "__main__":
    run()
