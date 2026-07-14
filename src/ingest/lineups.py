"""Derive on-court lineups per game from nbastats play-by-play via nba_on_court.

nba_on_court.players_on_court() calls np.in1d, removed in numpy>=2.0 (renamed
np.isin, same behavior) -- shim it rather than downgrade numpy project-wide.
"""

from pathlib import Path

import numpy as np

if not hasattr(np, "in1d"):
    np.in1d = np.isin

import nba_on_court as noc
import pandas as pd

RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"
PROCESSED_DIR = Path(__file__).resolve().parents[2] / "data" / "processed" / "lineups"

LINEUP_COLS = [f"{side}_PLAYER{i}" for side in ("HOME", "AWAY") for i in range(1, 6)]

# Games whose raw sub ledger is wholesale corrupt (missing/duplicated sub
# events; players with unbalanced in/out counts that no reordering repairs).
# The first four crash players_on_court outright; 22400860 derives silently
# wrong minutes (caught by check_team_minutes.py + box-score validation).
# 5 of 3690 games -- dropped and documented rather than patched, since
# pbpstats/data.nba.com live repair sources are unreachable from this machine.
CORRUPT_GAMES = {22200234, 22201040, 22400372, 22400433, 22400860}


def _repair_event_order(game_df: pd.DataFrame) -> pd.DataFrame:
    """Fix the two raw-feed corruption modes that break lineup derivation.

    (a) Isolated PERIOD-label glitches: a row chronologically inside period p
        but labeled p-1 (e.g. game 22301206 EVENTNUM 497/499). Detected as a
        period below the running max that is later followed by periods at or
        above that max; snapped up to the running max.
    (b) Corrupt EVENTNUMs: real events (usually subs) assigned an EVENTNUM
        that strands them away from their true position -- past the final
        buzzer (game 22200743 EVENTNUM 709/711) or inside a later period
        (game 22200053 EVENTNUM 473/474: Q3 subs amid early-Q4 rows). Their
        (PERIOD, clock) labels are correct, so a stable chronological sort
        reinserts them.

    The two modes look identical in EVENTNUM order (a lower-period row amid
    higher-period rows), so the clock disambiguates: only relabel a row as
    (a) when its clock fits where it sits; otherwise trust the label and let
    the sort move it, as in (b).
    """
    g = game_df.sort_values("EVENTNUM").reset_index(drop=True)

    clock = g["PCTIMESTRING"].astype(str).str.partition(":")
    remaining = (pd.to_numeric(clock[0]) * 60 + pd.to_numeric(clock[2])).to_numpy(dtype=float)

    def elapsed(period):
        start = np.where(period <= 4, (period - 1) * 720.0, 2880.0 + (period - 5) * 300.0)
        length = np.where(period <= 4, 720.0, 300.0)
        return start + (length - remaining)

    per = g["PERIOD"].to_numpy()
    prev_max = np.concatenate(([0], np.maximum.accumulate(per)[:-1]))
    suffix_max = np.concatenate((np.maximum.accumulate(per[::-1])[::-1][1:], [0]))
    candidate = (per < prev_max) & (suffix_max >= prev_max)

    # clock-consistency test: elapsed time under the relabeled period must fit
    # between the nearest trusted (non-candidate) neighbors, with slack for
    # clock jitter; NaN at the edges means no constraint on that side
    anchor = pd.Series(np.where(candidate, np.nan, elapsed(per)))
    prev_anchor = anchor.ffill().to_numpy()
    next_anchor = anchor.bfill().to_numpy()
    snapped = elapsed(prev_max)
    slack = 30.0
    fits = (
        (np.isnan(prev_anchor) | (snapped >= prev_anchor - slack))
        & (np.isnan(next_anchor) | (snapped <= next_anchor + slack))
    )
    g["PERIOD"] = np.where(candidate & fits, prev_max, per)

    g["_clock_desc"] = -remaining
    g = g.sort_values(["PERIOD", "_clock_desc"], kind="mergesort")
    g = g.drop(columns="_clock_desc").reset_index(drop=True)
    g["EVENT_ORDER"] = range(len(g))
    return g


def add_lineups_for_game(game_df: pd.DataFrame) -> pd.DataFrame:
    """Run players_on_court for one game's play-by-play.

    players_on_court() relies on input row order (not EVENTNUM value) for its
    internal per-period grouping and substitution-fill logic, and converts
    PCTIMESTRING to game-elapsed seconds using PERIOD -- so both row order and
    period labels must be repaired BEFORE this call; fixing them downstream
    cannot undo elapsed times baked in here.
    """
    ordered = _repair_event_order(game_df)
    result = noc.players_on_court(ordered)
    return result.sort_values("EVENT_ORDER").reset_index(drop=True)


def build_season_lineups(season: int) -> pd.DataFrame:
    """Add on-court lineups to every game in a season; cache the result to parquet."""
    out_path = PROCESSED_DIR / f"{season}.parquet"
    if out_path.exists():
        print(f"skip {season}: already built at {out_path}")
        return pd.read_parquet(out_path)

    raw_path = RAW_DIR / "nbastats" / str(season) / f"nbastats_{season}.csv"
    df = pd.read_csv(raw_path, low_memory=False)

    enriched_games = []
    failed_games = []
    for game_id, game_df in df.groupby("GAME_ID"):
        if game_id in CORRUPT_GAMES:
            print(f"  drop {game_id}: corrupt sub ledger (see CORRUPT_GAMES)")
            continue
        try:
            enriched_games.append(add_lineups_for_game(game_df))
        except Exception as e:
            failed_games.append((game_id, str(e)))

    if failed_games:
        print(f"{season}: {len(failed_games)} games failed lineup derivation:")
        for game_id, err in failed_games:
            print(f"  {game_id}: {err}")

    season_df = pd.concat(enriched_games, axis=0, ignore_index=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    season_df.to_parquet(out_path, index=False)
    print(f"{season}: {len(enriched_games)} games -> {out_path} ({len(season_df):,} rows)")
    return season_df


if __name__ == "__main__":
    for season in (2022, 2023, 2024):
        build_season_lineups(season)
