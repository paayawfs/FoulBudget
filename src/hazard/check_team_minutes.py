"""Free full-corpus screen for the exposure table: summed player minutes per
(game, team) must equal 5 x game length = 240 + 25 x n_OT. Needs no API calls,
so unlike validate_minutes.py's sampled box-score check it covers every game --
it is what surfaced the stuck-period/orphan-EVENTNUM bugs the 45-game sample
missed. Run after any exposure rebuild, before the box-score gate.
"""

from pathlib import Path

import pandas as pd

EXPOSURE_DIR = Path(__file__).resolve().parents[2] / "data" / "processed" / "exposure"
SEASONS = (2022, 2023, 2024)
# exposure spells end at the last recorded event, not the literal 0:00 buzzer
# (see exposure.py docstring), so team totals sit slightly under the physical
# maximum; 3 min/team absorbs that slack while still catching real breakage.
TOLERANCE_MINUTES = 3.0


def run() -> pd.DataFrame:
    dfs = [pd.read_parquet(EXPOSURE_DIR / f"{s}.parquet") for s in SEASONS]
    df = pd.concat(dfs, ignore_index=True)

    team_tot = df.groupby(["game_id", "team"])["minutes_exposed"].sum().reset_index(name="team_minutes")
    n_ot = (df.groupby("game_id")["period"].max() - 4).clip(lower=0).rename("n_ot")
    team_tot = team_tot.join(n_ot, on="game_id")
    team_tot["expected"] = 240 + 25 * team_tot["n_ot"]
    team_tot["diff"] = team_tot["team_minutes"] - team_tot["expected"]

    flagged = team_tot[team_tot["diff"].abs() > TOLERANCE_MINUTES]
    n_games = team_tot["game_id"].nunique()
    print(f"games checked: {n_games} | team-rows: {len(team_tot)}")
    print(f"diff quantiles (min): {team_tot['diff'].quantile([0.01, 0.25, 0.5, 0.75, 0.99]).round(2).to_dict()}")
    print(f"flagged (|diff| > {TOLERANCE_MINUTES} min): {len(flagged)} team-rows in {flagged['game_id'].nunique()} games")
    if not flagged.empty:
        print(flagged.sort_values("diff").head(30).to_string(index=False))
    return flagged


if __name__ == "__main__":
    run()
