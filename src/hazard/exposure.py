"""Build the player-stint exposure table from lineup-enriched play-by-play.

Per REFERENCE.md Section 3.3: each row is a continuous exposure spell for one
player at a fixed foul count within a fixed period, ending in either a foul
(fouls_in_window=1) or censoring (sub-out / period-end / game-end,
fouls_in_window=0). This is the counting-process framing the Poisson-with-
exposure model and the Cox robustness check both assume.

Known approximations (acceptable for the dev slice; revisit if the box-score
minutes reconciliation flags them):
  - period-end/game-end spells are timed to the last recorded event, not the
    literal 0:00 buzzer.
  - a spell ending in a foul and the following spell share the foul's
    timestamp (zero-duration state transition), matching the survival-
    analysis "recurrent event" framing rather than modeling dead time.
"""

from pathlib import Path

import pandas as pd

PROCESSED_LINEUPS_DIR = Path(__file__).resolve().parents[2] / "data" / "processed" / "lineups"
PROCESSED_EXPOSURE_DIR = Path(__file__).resolve().parents[2] / "data" / "processed" / "exposure"

HOME_COLS = [f"HOME_PLAYER{i}" for i in range(1, 6)]
AWAY_COLS = [f"AWAY_PLAYER{i}" for i in range(1, 6)]
FOUL_EVENTMSGTYPE = 6
SUB_EVENTMSGTYPE = 8
# EVENTMSGTYPE 6 action types that do NOT count toward the 6 personal fouls
# (technical variants, def-3-sec, delay, flopping, excess timeout) -- verified
# against the running personal count "(P#.T#)" in event descriptions; counting
# them pushes foul_count past the impossible 6.
NON_PERSONAL_FOUL_ACTIONS = {11, 12, 13, 16, 17, 18, 19, 25}


def _team_abbrev_map(game: pd.DataFrame) -> dict:
    """player_id -> team abbreviation, from every PLAYERn_ID/PLAYERn_TEAM_ABBREVIATION pair."""
    mapping = {}
    for i in (1, 2, 3):
        ids = game[f"PLAYER{i}_ID"]
        abbrevs = game[f"PLAYER{i}_TEAM_ABBREVIATION"]
        for pid, abbrev in zip(ids, abbrevs):
            if pid and pd.notna(abbrev):
                mapping[pid] = abbrev
    return mapping


def _score_margin(game: pd.DataFrame) -> pd.Series:
    margin = game["SCOREMARGIN"].replace("TIE", "0")
    return pd.to_numeric(margin, errors="coerce").ffill().fillna(0)


def _build_player_segments(game: pd.DataFrame, pid: int, side: str, team_abbrev: str, opp_abbrev: str) -> list:
    cols = HOME_COLS if side == "HOME" else AWAY_COLS
    on_court = (game[cols] == pid).any(axis=1)
    if not on_court.any():
        return []

    period_change = game["PERIOD"] != game["PERIOD"].shift()
    own_foul = (
        (game["EVENTMSGTYPE"] == FOUL_EVENTMSGTYPE)
        & (game["PLAYER1_ID"] == pid)
        & ~game["EVENTMSGACTIONTYPE"].isin(NON_PERSONAL_FOUL_ACTIONS)
    )
    sub_out_next = (game["EVENTMSGTYPE"] == SUB_EVENTMSGTYPE) & (game["PLAYER1_ID"] == pid)

    run_change = on_court != on_court.shift(fill_value=False)
    seg_break = on_court & (run_change | period_change | own_foul.shift(fill_value=False).fillna(False))
    seg_id = seg_break.cumsum()

    segments = []
    foul_count = 0
    elapsed = game["PCTIMESTRING"]
    margin = _score_margin(game)

    for _, seg in game[on_court].groupby(seg_id[on_court]):
        first_idx, last_idx = seg.index[0], seg.index[-1]
        start_time = elapsed.loc[first_idx]

        # anchor the start margin after stopped-clock activity at the spell's
        # opening resolves (free throws happen at a stopped clock): a spell
        # that begins right after this player's own foul must not have the
        # resulting opposing FTs booked into its margin_change -- that alone
        # fabricates a large negative "playing scared" effect
        same_clock = seg.index[elapsed.loc[seg.index] == start_time]
        anchor_idx = same_clock[-1]

        ends_in_foul = bool(own_foul.loc[last_idx])
        next_idx = last_idx + 1
        if ends_in_foul:
            ended_by = "foul"
            end_time = elapsed.loc[last_idx]
        elif next_idx in game.index and sub_out_next.loc[next_idx]:
            ended_by = "sub_out"
            end_time = elapsed.loc[next_idx]
        elif next_idx in game.index and game.loc[next_idx, "PERIOD"] != game.loc[last_idx, "PERIOD"]:
            ended_by = "period_end"
            end_time = elapsed.loc[last_idx]
        elif next_idx not in game.index:
            ended_by = "game_end"
            end_time = elapsed.loc[last_idx]
        else:
            ended_by = "unknown"
            end_time = elapsed.loc[last_idx]

        segments.append({
            "player_id": pid,
            "team": team_abbrev,
            "opponent": opp_abbrev,
            "side": side,
            "period": int(game.loc[first_idx, "PERIOD"]),
            "start_elapsed": start_time,
            "foul_count": foul_count,
            "score_margin": margin.loc[anchor_idx],
            # home-perspective margin change over the spell, from the post-
            # stopped-clock anchor to the spell's last event
            "margin_change": margin.loc[last_idx] - margin.loc[anchor_idx],
            "minutes_exposed": max(end_time - start_time, 0) / 60,
            "fouls_in_window": int(ends_in_foul),
            "ended_by": ended_by,
        })

        if ends_in_foul:
            foul_count += 1

    return segments


def build_game_exposure(game: pd.DataFrame) -> pd.DataFrame:
    """Exposure rows for every player in one lineup-enriched game.

    Event ordering and PERIOD-label repair happen upstream in
    src/ingest/lineups.py (_repair_event_order), before elapsed times are
    baked in -- EVENT_ORDER is that repaired chronological order.
    """
    game = game.sort_values("EVENT_ORDER").reset_index(drop=True)
    team_map = _team_abbrev_map(game)

    home_team = team_map.get(game[HOME_COLS[0]].iloc[0])
    away_team = team_map.get(game[AWAY_COLS[0]].iloc[0])

    rows = []
    home_players = pd.unique(game[HOME_COLS].values.ravel())
    away_players = pd.unique(game[AWAY_COLS].values.ravel())

    for pid in home_players:
        rows.extend(_build_player_segments(game, pid, "HOME", home_team, away_team))
    for pid in away_players:
        rows.extend(_build_player_segments(game, pid, "AWAY", away_team, home_team))

    df = pd.DataFrame(rows)
    df.insert(0, "game_id", game["GAME_ID"].iloc[0])
    return df


def build_season_exposure(season: int) -> pd.DataFrame:
    out_path = PROCESSED_EXPOSURE_DIR / f"{season}.parquet"
    if out_path.exists():
        print(f"skip {season}: already built at {out_path}")
        return pd.read_parquet(out_path)

    lineups_path = PROCESSED_LINEUPS_DIR / f"{season}.parquet"
    lineups = pd.read_parquet(lineups_path)

    game_tables = []
    failed_games = []
    for game_id, game in lineups.groupby("GAME_ID"):
        try:
            game_tables.append(build_game_exposure(game))
        except Exception as e:
            failed_games.append((game_id, str(e)))

    if failed_games:
        print(f"{season}: {len(failed_games)} games failed exposure build:")
        for game_id, err in failed_games:
            print(f"  {game_id}: {err}")

    season_df = pd.concat(game_tables, axis=0, ignore_index=True)
    PROCESSED_EXPOSURE_DIR.mkdir(parents=True, exist_ok=True)
    season_df.to_parquet(out_path, index=False)
    print(f"{season}: {len(game_tables)} games -> {out_path} ({len(season_df):,} rows)")
    return season_df


if __name__ == "__main__":
    for season in (2022, 2023, 2024):
        build_season_exposure(season)
