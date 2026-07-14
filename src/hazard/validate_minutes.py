"""Box-score-minutes reconciliation: the validation gate REFERENCE.md calls for
before any hazard modeling. Compares our derived exposure-table minutes per
(game, player) against the official box score, fetched live via nba_api for a
sample of games (not the full corpus -- this is a spot-check, not a bulk pull).
"""

import time
from pathlib import Path

import pandas as pd
from nba_api.stats.endpoints import boxscoretraditionalv2

EXPOSURE_DIR = Path(__file__).resolve().parents[2] / "data" / "processed" / "exposure"
OUT_PATH = Path(__file__).resolve().parents[2] / "reports" / "eda" / "minutes_reconciliation.csv"
SEASONS = (2022, 2023, 2024)
SAMPLE_PER_SEASON = 15
REQUEST_DELAY_SECONDS = 0.6
# regression set: every game the first validation run (pre event-order repair)
# flagged with systematic multi-player errors -- always re-checked so the
# repair in lineups.py can't silently regress.
REGRESSION_GAME_IDS = [
    22200006, 22200019, 22200053, 22200056, 22200505, 22200876,
    22300303, 22301206, 22400053, 22400654, 22400691, 22400860,
]


def load_derived_minutes() -> pd.DataFrame:
    dfs = [pd.read_parquet(EXPOSURE_DIR / f"{s}.parquet") for s in SEASONS]
    df = pd.concat(dfs, ignore_index=True)
    return df.groupby(["game_id", "player_id"])["minutes_exposed"].sum().reset_index(
        name="derived_minutes"
    )


def sample_game_ids() -> list:
    dfs = [pd.read_parquet(EXPOSURE_DIR / f"{s}.parquet") for s in SEASONS]
    ids = []
    for d in dfs:
        ids.extend(d["game_id"].drop_duplicates().sample(SAMPLE_PER_SEASON, random_state=0).tolist())
    # regression games dropped from the corpus (lineups.CORRUPT_GAMES) have no
    # derived minutes to reconcile
    present = set(pd.concat(dfs)["game_id"].unique())
    ids.extend(g for g in REGRESSION_GAME_IDS if g not in ids and g in present)
    return ids


def parse_min(min_str) -> float:
    if pd.isna(min_str) or min_str is None:
        return 0.0
    minutes, _, seconds = str(min_str).partition(":")
    return int(minutes) + int(seconds or 0) / 60


def fetch_official_minutes(game_id: int) -> pd.DataFrame:
    padded = f"{game_id:010d}"
    bx = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id=padded, timeout=20)
    df = bx.player_stats.get_data_frame()
    df["official_minutes"] = df["MIN"].apply(parse_min)
    df["game_id"] = game_id
    return df[["game_id", "PLAYER_ID", "official_minutes"]].rename(columns={"PLAYER_ID": "player_id"})


def run() -> pd.DataFrame:
    derived = load_derived_minutes()
    game_ids = sample_game_ids()

    official_frames = []
    failed = []
    for i, game_id in enumerate(game_ids):
        try:
            official_frames.append(fetch_official_minutes(game_id))
        except Exception as e:
            failed.append((game_id, str(e)))
        time.sleep(REQUEST_DELAY_SECONDS)
        if (i + 1) % 10 == 0:
            print(f"  fetched {i + 1}/{len(game_ids)}")

    if failed:
        print(f"{len(failed)} games failed to fetch:")
        for gid, err in failed:
            print(f"  {gid}: {err}")

    official = pd.concat(official_frames, ignore_index=True)
    merged = official.merge(derived, on=["game_id", "player_id"], how="left")
    merged["derived_minutes"] = merged["derived_minutes"].fillna(0.0)
    merged["error"] = merged["derived_minutes"] - merged["official_minutes"]
    merged["abs_error"] = merged["error"].abs()

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(OUT_PATH, index=False)

    print(f"\ngames sampled: {len(game_ids)}  |  player-game rows: {len(merged)}")
    print(f"mean absolute error: {merged['abs_error'].mean():.3f} minutes")
    print(f"median absolute error: {merged['abs_error'].median():.3f} minutes")
    for tol in (0.5, 1.0, 2.0):
        pct = (merged["abs_error"] <= tol).mean() * 100
        print(f"within {tol} min: {pct:.1f}%")

    # per-game clause: aggregate row stats can look fine while a systematic
    # per-game failure hits most of one game's players (the pre-repair state:
    # 81% of rows within 0.5 min, yet 12/45 games broken).
    per_game_bad = merged[merged["abs_error"] > 1.0].groupby("game_id").size()
    gate_ok = (
        (merged["abs_error"] <= 1.0).mean() >= 0.98
        and merged["abs_error"].max() <= 3.0
        and merged["abs_error"].mean() <= 0.3
        and (per_game_bad <= 1).all()
    )
    print(f"\ngames with >1 player off by >1 min: {(per_game_bad > 1).sum()}")
    print(f"VALIDATION GATE: {'PASS' if gate_ok else 'FAIL'} "
          f"(>=98% rows within 1 min, max error <=3 min, MAE <=0.3, "
          f"no game with 2+ players off by >1 min)")
    print(f"\nworst 10 discrepancies:")
    print(merged.sort_values("abs_error", ascending=False).head(10)[
        ["game_id", "player_id", "official_minutes", "derived_minutes", "error"]
    ].to_string(index=False))

    return merged


if __name__ == "__main__":
    run()
