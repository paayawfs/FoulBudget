"""Win-probability backbone W(d, t) per REFERENCE.md Section 3.1.

W(d, t) = P(home win | home score margin d, seconds remaining t), built from
every regulation-time event row in the lineup-enriched play-by-play. Two
estimators:
  - logistic in (d, d/sqrt(t), t) -- the smooth model the DP consumes
  - empirical bin-and-count table -- used to check the logistic's calibration
    (with only a 3-season dev slice the table itself is too sparse to be the
    primary; revisit when the full 20+ season corpus lands)

Fit on TRAIN_SEASONS, calibration reported on the held-out season
(REFERENCE.md Section 6). Writes model coefficients and the binned table to
data/processed/wp/.

ponytail: one row per pbp event, so high-event stretches (FT trips) weigh
slightly more than clean-flow stretches; switch to per-possession sampling if
calibration shows it matters.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

LINEUPS_DIR = Path(__file__).resolve().parents[2] / "data" / "processed" / "lineups"
OUT_DIR = Path(__file__).resolve().parents[2] / "data" / "processed" / "wp"
TRAIN_SEASONS = (2022, 2023)
HOLDOUT_SEASON = 2024
REGULATION_SECONDS = 2880
TIME_BIN_SECONDS = 30
MARGIN_CLIP = 30


def load_states(season: int) -> pd.DataFrame:
    """One row per event: (game_id, seconds remaining, home margin, home won)."""
    df = pd.read_parquet(
        LINEUPS_DIR / f"{season}.parquet",
        columns=["GAME_ID", "PCTIMESTRING", "SCOREMARGIN"],
    )
    margin = df["SCOREMARGIN"].replace("TIE", "0")
    df["margin"] = pd.to_numeric(margin, errors="coerce")
    df["margin"] = df.groupby("GAME_ID")["margin"].ffill().fillna(0)

    final = df.groupby("GAME_ID")["margin"].last()
    df["home_won"] = (df["GAME_ID"].map(final) > 0).astype(int)

    df = df[df["PCTIMESTRING"] <= REGULATION_SECONDS]
    out = pd.DataFrame({
        "game_id": df["GAME_ID"],
        "t_remaining": REGULATION_SECONDS - df["PCTIMESTRING"],
        "margin": df["margin"].clip(-MARGIN_CLIP, MARGIN_CLIP),
        "home_won": df["home_won"],
    })
    return out


def design_matrix(states: pd.DataFrame) -> np.ndarray:
    d = states["margin"].to_numpy(dtype=float)
    t = states["t_remaining"].to_numpy(dtype=float)
    return sm.add_constant(
        np.column_stack([d, d / np.sqrt(t + 1.0), t]), has_constant="add"
    )


def fit(states: pd.DataFrame):
    return sm.Logit(states["home_won"], design_matrix(states)).fit(disp=False)


def binned_table(states: pd.DataFrame) -> pd.DataFrame:
    b = states.copy()
    b["t_bin"] = (b["t_remaining"] // TIME_BIN_SECONDS) * TIME_BIN_SECONDS
    g = b.groupby(["t_bin", "margin"])["home_won"].agg(["mean", "count"])
    return g.reset_index().rename(columns={"mean": "wp", "count": "n"})


def calibration_report(model, states: pd.DataFrame) -> pd.DataFrame:
    """Predicted vs actual home-win rate in predicted-probability deciles."""
    p = model.predict(design_matrix(states))
    rep = pd.DataFrame({"p": p, "y": states["home_won"].to_numpy()})
    rep["bucket"] = (rep["p"] * 10).clip(0, 9).astype(int)
    out = rep.groupby("bucket").agg(pred=("p", "mean"), actual=("y", "mean"), n=("y", "size"))
    out["gap"] = out["actual"] - out["pred"]
    return out


def run() -> None:
    train = pd.concat([load_states(s) for s in TRAIN_SEASONS], ignore_index=True)
    holdout = load_states(HOLDOUT_SEASON)
    print(f"train rows: {len(train):,} ({TRAIN_SEASONS})  |  holdout rows: {len(holdout):,} ({HOLDOUT_SEASON})")

    model = fit(train)
    print("\nlogistic coefficients [const, d, d/sqrt(t), t]:")
    print(model.params.round(6).tolist())

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pd.Series(model.params).to_csv(OUT_DIR / "logit_coefs.csv", header=False)
    binned_table(train).to_parquet(OUT_DIR / "binned_table.parquet", index=False)

    rep = calibration_report(model, holdout)
    print(f"\ncalibration on held-out {HOLDOUT_SEASON} (predicted-prob deciles):")
    print(rep.round(4).to_string())
    worst = rep["gap"].abs().max()
    print(f"\nworst decile gap: {worst:.4f}  ({'OK' if worst < 0.03 else 'CHECK'} at 3pp tolerance)")

    # sanity anchors
    anchors = pd.DataFrame({
        "margin": [0.0, 5.0, -5.0, 10.0, 0.0],
        "t_remaining": [2880.0, 600.0, 600.0, 60.0, 1.0],
    })
    X = sm.add_constant(np.column_stack([
        anchors["margin"],
        anchors["margin"] / np.sqrt(anchors["t_remaining"] + 1.0),
        anchors["t_remaining"],
    ]), has_constant="add")
    anchors["wp"] = model.predict(X)
    print("\nsanity anchors (home perspective):")
    print(anchors.to_string(index=False))


if __name__ == "__main__":
    run()
