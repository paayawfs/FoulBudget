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
CORRUPT_GAMES = {22100545, 22200234, 22201040, 22400372, 22400433, 22400860}


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


def _cdn_as_v2(season: int) -> pd.DataFrame:
    """Adapt the cdnnba (data.nba.com live) format to the v2 columns this
    pipeline consumes. Needed for 2025-26+, which shufinskiy publishes only
    in v3/cdn form; cdn is preferred over v3 because substitutions carry
    both player IDs (v3 names the incoming player only in free text).
    """
    raw = pd.read_csv(RAW_DIR / "cdnnba" / str(season) / f"cdnnba_{season}.csv",
                      low_memory=False)
    raw = raw.sort_values(["gameId", "orderNumber"]).reset_index(drop=True)

    clock = raw["clock"].str.extract(r"PT(\d+)M(\d+)")
    pctime = clock[0].astype(int).astype(str) + ":" + clock[1].str.zfill(2)

    msg = pd.Series(0, index=raw.index)  # default: irrelevant event type
    msg[raw["actionType"] == "foul"] = 6
    msg[(raw["actionType"] == "period") & (raw["subType"] == "start")] = 12
    msg[(raw["actionType"] == "period") & (raw["subType"] == "end")] = 13

    # cdn folds every non-personal foul into subType "technical"; map it to
    # v2 action type 11 (in exposure's NON_PERSONAL_FOUL_ACTIONS), rest to 1
    action = pd.Series(0, index=raw.index)
    action[(msg == 6) & (raw["subType"] == "technical")] = 11
    action[(msg == 6) & (raw["subType"] != "technical")] = 1

    player_ids = raw["personId"].fillna(0).astype(np.int64)
    is_player = (player_ids > 0) & (player_ids < 10**9)  # team ids are 161061xxxx

    # PERSONxTYPE must encode the side (4 = home player, 5 = away player) --
    # nba_on_court splits HOME/AWAY lineups on it. cdn has no home flag, but
    # scoreHome increments exactly when the acting team is the home team.
    dh = raw.groupby("gameId")["scoreHome"].diff().fillna(0)
    home_scoring = raw.loc[(dh > 0) & raw["teamId"].notna(), ["gameId", "teamId"]]
    home_team = home_scoring.groupby("gameId")["teamId"].agg(lambda s: s.mode().iloc[0])
    row_is_home = raw["teamId"] == raw["gameId"].map(home_team)

    df = pd.DataFrame({
        "GAME_ID": raw["gameId"],
        "EVENTNUM": raw["orderNumber"],  # guaranteed monotone, unlike v2
        "EVENTMSGTYPE": msg,
        "EVENTMSGACTIONTYPE": action,
        "PERIOD": raw["period"],
        "PCTIMESTRING": pctime,
        "SCOREMARGIN": (raw["scoreHome"] - raw["scoreAway"]).astype("Int64").astype(str),
        "SCORE": raw["scoreAway"].astype("Int64").astype(str) + " - " + raw["scoreHome"].astype("Int64").astype(str),
        "PERSON1TYPE": np.where(is_player, np.where(row_is_home, 4, 5), 7),  # noc ignores 6/7
        "PLAYER1_ID": player_ids.where(is_player, 0),
        "PLAYER1_NAME": raw["playerNameI"],
        "PLAYER1_TEAM_ABBREVIATION": raw["teamTricode"],
        "PERSON2TYPE": 0, "PLAYER2_ID": 0, "PLAYER2_NAME": None, "PLAYER2_TEAM_ABBREVIATION": None,
        "PERSON3TYPE": 0, "PLAYER3_ID": 0, "PLAYER3_NAME": None, "PLAYER3_TEAM_ABBREVIATION": None,
    })

    # collapse out/in substitution rows into single v2-style sub rows
    # (PLAYER1 = out, PLAYER2 = in). Mass substitutions arrive as blocks of
    # outs followed by ins, so pair positionally WITHIN each
    # (game, team, period, clock) stoppage rather than by adjacency.
    keys = ["gameId", "teamId", "period", "clock"]
    subs = raw.loc[raw["actionType"] == "substitution", keys + ["subType", "personId", "playerNameI", "teamTricode"]].copy()
    subs["rank"] = subs.groupby(keys + ["subType"]).cumcount()
    outs = subs[subs["subType"] == "out"].reset_index()
    ins = subs[subs["subType"] == "in"].reset_index()
    m = outs.merge(ins, on=keys + ["rank"], suffixes=("_o", "_i"))
    df.loc[m["index_o"], "EVENTMSGTYPE"] = 8
    # sub-in player is on the same side as the sub-out player
    df.loc[m["index_o"], "PERSON2TYPE"] = df.loc[m["index_o"], "PERSON1TYPE"].to_numpy()
    df.loc[m["index_o"], "PLAYER2_ID"] = m["personId_i"].to_numpy(dtype=np.int64)
    df.loc[m["index_o"], "PLAYER2_NAME"] = m["playerNameI_i"].to_numpy()
    df.loc[m["index_o"], "PLAYER2_TEAM_ABBREVIATION"] = m["teamTricode_i"].to_numpy()
    unpaired = len(outs) + len(ins) - 2 * len(m)
    if unpaired:
        print(f"  cdn adapter: {unpaired} substitution rows unmatched within their stoppage (left as non-events)")

    # cdn additionally announces period-START lineup changes as subs at the
    # untouched clock (12:00, or 5:00 in OT); v2 never does, and nba_on_court
    # infers period lineups from play instead -- feeding it these breaks its
    # per-period player inference, so demote them back to non-events
    start_clock = np.where(m["period"] <= 4, "PT12M00.00S", "PT05M00.00S")
    admin = m.loc[m["clock"].to_numpy() == start_clock, "index_o"]
    df.loc[admin, "EVENTMSGTYPE"] = 0
    # matched 'in' rows stay EVENTMSGTYPE 0 (consumed by the pair)

    df["SCOREMARGIN"] = df["SCOREMARGIN"].replace("<NA>", None)
    return df


def build_season_lineups(season: int) -> pd.DataFrame:
    """Add on-court lineups to every game in a season; cache the result to parquet."""
    out_path = PROCESSED_DIR / f"{season}.parquet"
    if out_path.exists():
        print(f"skip {season}: already built at {out_path}")
        return pd.read_parquet(out_path)

    raw_path = RAW_DIR / "nbastats" / str(season) / f"nbastats_{season}.csv"
    if raw_path.exists():
        df = pd.read_csv(raw_path, low_memory=False)
    else:
        print(f"{season}: no v2 nbastats file, adapting cdnnba")
        df = _cdn_as_v2(season)

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
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from config import RAPM_SEASONS
    for season in RAPM_SEASONS:
        build_season_lineups(season)
