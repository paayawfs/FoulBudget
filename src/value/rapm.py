"""Self-built RAPM with exponential time decay per REFERENCE.md Section 3.2.

Stints = maximal runs of one fixed 10-player lineup, from the lineup-enriched
play-by-play. Weighted ridge regression: y = home-margin change per minute,
X = +1 home players / -1 away players, unpenalized intercept for home
advantage. Coefficients read as net points per minute vs league average --
the scale delta_i needs.

For a target season, all stints from that season and earlier are pooled and
weighted by minutes x 0.5^(age / HALFLIFE_SEASONS), age measured from the
stint to the end of the target season (game sequence number gives
within-season chronology). Recent play dominates; older seasons stabilize
thin samples. This settles Section 3.5's single- vs multi-season question
with a decay prior. Reported `minutes` remain the target season's alone, so
downstream eligibility filters keep their meaning.

Ridge alpha picked by 2-fold CV over games (per target season). Output:
data/processed/value/rapm_{season}.csv with player_id, name, rapm, minutes.

ponytail: per-minute rates, not per-possession -- pace is a mild confounder;
upgrade to possession-denominated stints if archetype results look
pace-driven.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import sparse

LINEUPS_DIR = Path(__file__).resolve().parents[2] / "data" / "processed" / "lineups"
OUT_DIR = Path(__file__).resolve().parents[2] / "data" / "processed" / "value"
SEASONS = (2022, 2023, 2024)
HOME_COLS = [f"HOME_PLAYER{i}" for i in range(1, 6)]
AWAY_COLS = [f"AWAY_PLAYER{i}" for i in range(1, 6)]
ALPHA_GRID = (250.0, 1000.0, 4000.0, 16000.0)
HALFLIFE_SEASONS = 1.0     # stint weight halves per season of age
GAMES_PER_SEASON = 1230    # sequence number -> within-season fraction


def build_stints(season: int) -> pd.DataFrame:
    cols = ["GAME_ID", "EVENT_ORDER", "PCTIMESTRING", "SCOREMARGIN"] + HOME_COLS + AWAY_COLS
    df = pd.read_parquet(LINEUPS_DIR / f"{season}.parquet", columns=cols)
    df = df.sort_values(["GAME_ID", "EVENT_ORDER"])
    df["margin"] = pd.to_numeric(df["SCOREMARGIN"].replace("TIE", "0"), errors="coerce")
    df["margin"] = df.groupby("GAME_ID")["margin"].ffill().fillna(0)

    lineup_change = (
        df[HOME_COLS + AWAY_COLS].ne(df[HOME_COLS + AWAY_COLS].shift()).any(axis=1)
        | df["GAME_ID"].ne(df["GAME_ID"].shift())
    )
    df["stint_id"] = lineup_change.cumsum()

    g = df.groupby("stint_id")
    stints = g.agg(
        game_id=("GAME_ID", "first"),
        end_elapsed=("PCTIMESTRING", "last"),
        end_margin=("margin", "last"),
        **{c: (c, "first") for c in HOME_COLS + AWAY_COLS},
    )
    prev = stints.groupby("game_id")[["end_elapsed", "end_margin"]].shift()
    stints["minutes"] = (stints["end_elapsed"] - prev["end_elapsed"].fillna(0)) / 60
    stints["dmargin"] = stints["end_margin"] - prev["end_margin"].fillna(0)
    return stints[stints["minutes"] > 0].reset_index(drop=True)


def design(stints: pd.DataFrame):
    players = np.unique(stints[HOME_COLS + AWAY_COLS].to_numpy().ravel())
    col = {p: i for i, p in enumerate(players)}
    n = len(stints)
    rows = np.repeat(np.arange(n), 10)
    cols_idx = np.array([col[p] for p in stints[HOME_COLS + AWAY_COLS].to_numpy().ravel()])
    vals = np.tile([1.0] * 5 + [-1.0] * 5, n)
    X = sparse.csr_matrix((vals, (rows, cols_idx)), shape=(n, len(players)))
    # unpenalized intercept column appended last
    X = sparse.hstack([X, np.ones((n, 1))]).tocsr()
    return X, players


def ridge_solve(X, y, w, alpha: float) -> np.ndarray:
    Xw = X.multiply(w[:, None])
    A = (X.T @ Xw).toarray()
    pen = np.full(X.shape[1], alpha)
    pen[-1] = 0.0  # intercept unpenalized
    A[np.diag_indices_from(A)] += pen
    b = X.T @ (w * y)
    return np.linalg.solve(A, b)


def fit_season(season: int, stints_by_season: dict) -> pd.DataFrame:
    pooled = []
    for s, st in stints_by_season.items():
        if s <= season:
            pooled.append(st.assign(season=s))
    stints = pd.concat(pooled, ignore_index=True)

    # age in seasons from the stint to the end of the target season; the
    # game sequence number (GAME_ID % 100000) increments chronologically
    seq_frac = (stints["game_id"] % 100000).clip(upper=GAMES_PER_SEASON) / GAMES_PER_SEASON
    age = (season + 1.0) - (stints["season"] + seq_frac)
    decay = 0.5 ** (age.to_numpy() / HALFLIFE_SEASONS)

    X, players = design(stints)
    y = (stints["dmargin"] / stints["minutes"]).to_numpy()
    w = stints["minutes"].to_numpy() * decay

    fold = (stints["game_id"].to_numpy() % 2).astype(bool)
    best_alpha, best_mse = None, np.inf
    for alpha in ALPHA_GRID:
        mse = 0.0
        for train_mask in (fold, ~fold):
            beta = ridge_solve(X[train_mask], y[train_mask], w[train_mask], alpha)
            resid = y[~train_mask] - X[~train_mask] @ beta
            mse += float((w[~train_mask] * resid**2).sum() / w[~train_mask].sum())
        if mse < best_mse:
            best_alpha, best_mse = alpha, mse

    beta = ridge_solve(X, y, w, best_alpha)

    # raw minutes in the target season only, so eligibility filters and the
    # replacement composites keep their per-season meaning
    tgt = stints_by_season[season]
    on_ids = tgt[HOME_COLS + AWAY_COLS].to_numpy().ravel()
    tgt_minutes = pd.Series(np.repeat(tgt["minutes"].to_numpy(), 10)).groupby(on_ids).sum()

    out = pd.DataFrame({
        "player_id": players,
        "rapm": beta[:-1],
    })
    out["minutes"] = out["player_id"].map(tgt_minutes).fillna(0.0)
    print(f"{season}: {len(stints):,} pooled stints "
          f"(halflife {HALFLIFE_SEASONS:g} season), {len(players)} players, "
          f"alpha={best_alpha:g}, home-adv intercept={beta[-1]*48:.2f} pts/48")
    return out


def player_names(season: int) -> pd.Series:
    df = pd.read_parquet(
        LINEUPS_DIR / f"{season}.parquet", columns=["PLAYER1_ID", "PLAYER1_NAME"]
    ).dropna().drop_duplicates("PLAYER1_ID")
    return df.set_index("PLAYER1_ID")["PLAYER1_NAME"]


def run() -> None:
    # Windows cp1252 console can't print diacritics in player names
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stints_by_season = {s: build_stints(s) for s in SEASONS}
    for season in SEASONS:
        out = fit_season(season, stints_by_season)
        names = player_names(season)
        out["name"] = out["player_id"].map(names)
        out.to_csv(OUT_DIR / f"rapm_{season}.csv", index=False)

        heavy = out[out["minutes"] >= 1000].copy()
        heavy["rapm_per48"] = heavy["rapm"] * 48
        print(f"  top 10 (>=1000 min), pts/48 vs avg:")
        print(heavy.nlargest(10, "rapm")[["name", "rapm_per48", "minutes"]]
              .round(2).to_string(index=False))
        print()


if __name__ == "__main__":
    run()
