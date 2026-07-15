"""Empirical replacement composites and delta per REFERENCE.md Section 3.2.

For each substitution event "B replaces A", B absorbs A's minutes until B next
leaves the floor; per player-season, w_ij = j's minutes-weighted share of i's
replacement minutes. Then

    delta_i = RAPM_i - sum_j w_ij * RAPM_j

Because the composite reflects observed coach behavior, delta prices the real
decision: "play him" vs "whatever coaches demonstrably do instead."

Outputs per season: replacement_weights_{season}.csv, delta_{season}.csv.

ponytail: weights use ALL substitutions, not just foul-trouble ones -- the
foul-trouble-conditioned refinement (Section 3.2) waits until sub events are
tabulated enough to set its sample-size fallback. Mass-sub pairing noise is
documented as a limitation, smoothed by minutes-weighting.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

LINEUPS_DIR = Path(__file__).resolve().parents[2] / "data" / "processed" / "lineups"
VALUE_DIR = Path(__file__).resolve().parents[2] / "data" / "processed" / "value"
import sys as _sys
_sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import ANALYSIS_SEASONS as SEASONS
ON_COLS = [f"{side}_PLAYER{i}" for side in ("HOME", "AWAY") for i in range(1, 6)]
SUB_EVENTMSGTYPE = 8


def game_replacement_minutes(game: pd.DataFrame) -> list:
    """(out_player, in_player, minutes B stayed on) per sub event in one game."""
    on = game[ON_COLS].to_numpy()
    elapsed = game["PCTIMESTRING"].to_numpy()
    end_elapsed = elapsed[-1]
    out = []
    subs = np.flatnonzero(game["EVENTMSGTYPE"].to_numpy() == SUB_EVENTMSGTYPE)
    for i in subs:
        a, b = game["PLAYER1_ID"].iat[i], game["PLAYER2_ID"].iat[i]
        on_b = (on[i + 1:] == b).any(axis=1)
        off = np.flatnonzero(~on_b)
        leave = elapsed[i + 1 + off[0]] if len(off) else end_elapsed
        out.append((a, b, max(leave - elapsed[i], 0) / 60))
    return out


def build_weights(season: int) -> pd.DataFrame:
    cols = ["GAME_ID", "EVENT_ORDER", "EVENTMSGTYPE", "PCTIMESTRING",
            "PLAYER1_ID", "PLAYER2_ID"] + ON_COLS
    df = pd.read_parquet(LINEUPS_DIR / f"{season}.parquet", columns=cols)
    df = df.sort_values(["GAME_ID", "EVENT_ORDER"])

    rows = []
    for _, game in df.groupby("GAME_ID"):
        rows.extend(game_replacement_minutes(game.reset_index(drop=True)))
    ev = pd.DataFrame(rows, columns=["player_id", "replacement_id", "minutes"])

    agg = ev.groupby(["player_id", "replacement_id"]).agg(
        minutes=("minutes", "sum"), n_events=("minutes", "size")
    ).reset_index()
    total = agg.groupby("player_id")["minutes"].transform("sum")
    agg["weight"] = agg["minutes"] / total
    return agg


def build_delta(season: int, weights: pd.DataFrame) -> pd.DataFrame:
    rapm = pd.read_csv(VALUE_DIR / f"rapm_{season}.csv")
    r = rapm.set_index("player_id")["rapm"]

    w = weights.copy()
    w["repl_rapm"] = w["replacement_id"].map(r)
    composite = (
        w.dropna(subset=["repl_rapm"])
        .groupby("player_id")
        .apply(lambda g: np.average(g["repl_rapm"], weights=g["weight"]), include_groups=False)
        .rename("composite_rapm")
    )

    out = rapm.join(composite, on="player_id")
    out["delta"] = out["rapm"] - out["composite_rapm"]
    # robustness spec (Section 3.2): delta vs league average = raw RAPM
    out["delta_vs_avg"] = out["rapm"]
    return out


def run() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    for season in SEASONS:
        weights = build_weights(season)
        weights.to_csv(VALUE_DIR / f"replacement_weights_{season}.csv", index=False)
        delta = build_delta(season, weights)
        delta.to_csv(VALUE_DIR / f"delta_{season}.csv", index=False)

        heavy = delta[delta["minutes"] >= 1500].copy()
        heavy["delta_per48"] = heavy["delta"] * 48
        print(f"{season}: {len(weights):,} replacement pairs | "
              f"median composite (pts/48): {delta['composite_rapm'].median() * 48:.2f}")
        print("  largest play/sit gaps (>=1500 min), pts/48:")
        print(heavy.nlargest(8, "delta")[["name", "delta_per48", "minutes"]]
              .round(2).to_string(index=False))
        print()


if __name__ == "__main__":
    run()
