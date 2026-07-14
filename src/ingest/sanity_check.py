"""Download-level sanity check for the nbastats/pbpstats dev slice.

Not the stint/box-score reconciliation validation gate (that comes once the
exposure table exists) -- just confirms the raw archives are complete and
parseable before building anything on top of them.
"""

from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"
SEASONS = [2022, 2023, 2024]
EXPECTED_REGULAR_SEASON_GAMES = 1230  # 30 teams x 82 games / 2


def check_nbastats(season: int) -> pd.DataFrame:
    path = DATA_DIR / "nbastats" / str(season) / f"nbastats_{season}.csv"
    df = pd.read_csv(path, low_memory=False)
    n_games = df["GAME_ID"].nunique()
    size_mb = path.stat().st_size / 1e6
    print(f"nbastats {season}: {len(df):>9,} rows | {n_games:>4} unique games | {size_mb:6.1f} MB")
    if abs(n_games - EXPECTED_REGULAR_SEASON_GAMES) > 5:
        print(f"  ! game count {n_games} deviates from expected ~{EXPECTED_REGULAR_SEASON_GAMES}")
    return df


def check_pbpstats(season: int) -> pd.DataFrame:
    path = DATA_DIR / "pbpstats" / str(season) / f"pbpstats_{season}.csv"
    df = pd.read_csv(path, low_memory=False)
    n_games = df["GAMEID"].nunique()
    size_mb = path.stat().st_size / 1e6
    print(f"pbpstats {season}: {len(df):>9,} rows | {n_games:>4} unique games | {size_mb:6.1f} MB")
    if abs(n_games - EXPECTED_REGULAR_SEASON_GAMES) > 5:
        print(f"  ! game count {n_games} deviates from expected ~{EXPECTED_REGULAR_SEASON_GAMES}")
    return df


def spot_check_game(nbastats_df: pd.DataFrame, season: int) -> None:
    game_id = nbastats_df["GAME_ID"].iloc[len(nbastats_df) // 2]
    game = nbastats_df[nbastats_df["GAME_ID"] == game_id].sort_values("EVENTNUM")

    print(f"\nspot check {season} game {game_id} ({len(game)} events):")
    print(f"  periods present: {sorted(game['PERIOD'].unique().tolist())}")
    print(f"  final score row: {game['SCORE'].dropna().iloc[-1]}")

    fouls = game[game["EVENTMSGTYPE"] == 6]
    print(f"  foul events: {len(fouls)}")
    if not fouls.empty:
        sample = fouls.iloc[0]
        description = sample["HOMEDESCRIPTION"] if pd.notna(sample["HOMEDESCRIPTION"]) else sample["VISITORDESCRIPTION"]
        print(f"  sample foul: {sample['PLAYER1_NAME']} ({sample['PLAYER1_TEAM_ABBREVIATION']}), "
              f"Q{sample['PERIOD']} {sample['PCTIMESTRING']}: {description}")

    subs = game[game["EVENTMSGTYPE"] == 8]
    print(f"  substitution events: {len(subs)}")


def main() -> None:
    for season in SEASONS:
        nbastats_df = check_nbastats(season)
        check_pbpstats(season)
        spot_check_game(nbastats_df, season)
        print()


if __name__ == "__main__":
    main()
