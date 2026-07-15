"""Cox proportional-hazards robustness check per REFERENCE.md Section 3.3.

Same counting-process rows as the Poisson model: duration = spell minutes,
event = spell ended in a foul, censoring at sub-out/period-end/game-end.
Player heterogeneity enters as the fitted Poisson alpha_i included as a
covariate (lifelines has no offsets; its coefficient should land near 1 if
the two likelihoods agree).

SEs are naive: lifelines' cluster-robust computation is intractable at 444k
rows (hours; killed twice), and this check only compares point estimates
against the Poisson -- inference lives there.

The check passes if exp(coef) on the foul terms lands near the Poisson's
(x0.95 per foul carried / x0.66 in foul trouble).
"""

import sys
from pathlib import Path

import pandas as pd
from lifelines import CoxPHFitter

EXPOSURE_DIR = Path(__file__).resolve().parents[2] / "data" / "processed" / "exposure"
HAZARD_DIR = Path(__file__).resolve().parents[2] / "data" / "processed" / "hazard"
import sys as _sys
_sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import ANALYSIS_SEASONS as SEASONS


def load() -> pd.DataFrame:
    df = pd.concat(
        [pd.read_parquet(EXPOSURE_DIR / f"{s}.parquet").assign(season=s) for s in SEASONS],
        ignore_index=True,
    )
    df = df[df["minutes_exposed"] > 0].copy()
    df["player_season"] = df["player_id"].astype(str) + "_" + df["season"].astype(str)
    alphas = pd.read_csv(HAZARD_DIR / "alphas.csv", index_col=0)["alpha"]
    df["alpha_poisson"] = df["player_season"].map(alphas).fillna(alphas.mean())
    df["foul_trouble"] = (df["foul_count"] >= df["period"] + 1).astype(float)
    df["abs_margin"] = df["score_margin"].abs()
    for p in (2, 3, 4, 5):
        df[f"p_{p}"] = (df["period"].clip(upper=5) == p).astype(float)
    return df


def run() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    df = load()
    base_cols = ["alpha_poisson", "abs_margin", "p_2", "p_3", "p_4", "p_5"]

    for foul_term in ("foul_count", "foul_trouble"):
        cols = [foul_term] + base_cols
        cph = CoxPHFitter()
        cph.fit(
            df[cols + ["minutes_exposed", "fouls_in_window"]],
            duration_col="minutes_exposed",
            event_col="fouls_in_window",
        )
        s = cph.summary.loc[cols, ["coef", "exp(coef)", "se(coef)"]]
        print(f"\n=== Cox, foul term: {foul_term} ===")
        print(s.round(4).to_string())


if __name__ == "__main__":
    run()
