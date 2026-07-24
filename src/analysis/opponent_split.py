"""E8 opponent-strength robustness split of the convention cost.

Panel A (primary): tag each evaluated foul-trouble occurrence with the
OPPONENT's team-season net rating (points scored minus allowed per 100
possessions at the league-pace possession convention, 100/48 per minute --
identical to net points per 48) computed from the lineup-enriched
play-by-play, split into terciles, and report mean WP cost per occurrence
at estimated kappa and at kappa = 0.

Panel B (secondary): same terciles on the summed RAPM of the five opponent
players on the floor at the decision moment (the occurrence's spell,
sampled mid-spell so the lineup is unambiguous), using that season's
ratings (decay burn-in rules unchanged). This split correlates with score
state -- weak lineups appear in blowouts -- so Panel A is the primary
evidence.

Pass condition (pre-registered): mean cost per occurrence is positive in
every tercile of Panel A at kappa = 0.

Outputs:
  reports/e8_opponent_split.md
  data/processed/analysis/e8_meta.json (consumed by tests/run_validation.py)
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from config import ANALYSIS_SEASONS, EVAL_SEASON  # noqa: E402
from policy.solver import margin_step_distribution, evaluate_convention_cost  # noqa: E402

LINEUPS_DIR = ROOT / "data" / "processed" / "lineups"
EXPOSURE_DIR = ROOT / "data" / "processed" / "exposure"
HAZARD_DIR = ROOT / "data" / "processed" / "hazard"
VALUE_DIR = ROOT / "data" / "processed" / "value"
OUT_MD = ROOT / "reports" / "e8_opponent_split.md"
OUT_META = ROOT / "data" / "processed" / "analysis" / "e8_meta.json"
HOME_COLS = [f"HOME_PLAYER{i}" for i in range(1, 6)]
AWAY_COLS = [f"AWAY_PLAYER{i}" for i in range(1, 6)]
TERCILE_LABELS = ["weak", "average", "strong"]


def team_season_net_ratings() -> pd.DataFrame:
    """Net rating per team-season over the behavioral window, from final
    scores and game minutes in the lineup-enriched play-by-play."""
    rows = []
    for s in ANALYSIS_SEASONS:
        lu = pd.read_parquet(LINEUPS_DIR / f"{s}.parquet",
                             columns=["GAME_ID", "PCTIMESTRING", "SCORE"])
        lu = lu.dropna(subset=["SCORE"])
        last = lu.groupby("GAME_ID").last()
        scores = last["SCORE"].str.split("-", expand=True).astype(int)
        last["away_pts"], last["home_pts"] = scores[0], scores[1]
        last["minutes"] = lu.groupby("GAME_ID")["PCTIMESTRING"].max() / 60

        ex = pd.read_parquet(EXPOSURE_DIR / f"{s}.parquet",
                             columns=["game_id", "team", "side"])
        sides = ex.drop_duplicates(["game_id", "side"]).pivot(
            index="game_id", columns="side", values="team")
        g = last.join(sides)
        for side, opp_side, pts, opp_pts in (("HOME", "AWAY", "home_pts", "away_pts"),
                                             ("AWAY", "HOME", "away_pts", "home_pts")):
            rows.append(pd.DataFrame({
                "season": s, "team": g[side], "pts_for": g[pts],
                "pts_against": g[opp_pts], "minutes": g["minutes"]}))
    per_game = pd.concat(rows, ignore_index=True)
    ts = per_game.groupby(["season", "team"], as_index=False).sum()
    ts["net100"] = (ts["pts_for"] - ts["pts_against"]) / ts["minutes"] * 48
    return ts


def occurrence_frame(costs_est: pd.DataFrame, costs_k0: pd.DataFrame) -> pd.DataFrame:
    """Merge est/k0 costs and attach opponent + spell timing from the
    exposure table (same first-trouble-spell definition as the solver)."""
    ex = pd.read_parquet(EXPOSURE_DIR / f"{EVAL_SEASON}.parquet")
    ex = ex[ex["minutes_exposed"] > 0]
    trouble = ex[ex["foul_count"] >= ex["period"] + 1]
    first = (trouble.sort_values("start_elapsed")
             .groupby(["game_id", "player_id"]).first().reset_index())
    occ = costs_est.merge(
        costs_k0[["game_id", "player_id", "cost_wp"]].rename(columns={"cost_wp": "cost_wp_k0"}),
        on=["game_id", "player_id"])
    occ = occ.merge(first[["game_id", "player_id", "opponent", "side",
                           "start_elapsed", "minutes_exposed", "score_margin"]],
                    on=["game_id", "player_id"])
    assert len(occ) == len(costs_est), "occurrence merge changed row count"
    return occ


def opponent_lineup_rapm(occ: pd.DataFrame) -> pd.DataFrame:
    """Summed RAPM of the five opponent players on floor mid-spell."""
    lu = pd.read_parquet(LINEUPS_DIR / f"{EVAL_SEASON}.parquet",
                         columns=["GAME_ID", "EVENT_ORDER", "PCTIMESTRING"]
                         + HOME_COLS + AWAY_COLS)
    lu = lu.sort_values(["GAME_ID", "EVENT_ORDER"])
    lu["PCTIMESTRING"] = lu["PCTIMESTRING"].astype(float)

    occ = occ.copy()
    occ["mid_elapsed"] = occ["start_elapsed"] + occ["minutes_exposed"] * 30  # half the spell, in sec
    occ = occ.sort_values("mid_elapsed")
    merged = pd.merge_asof(occ, lu.sort_values("PCTIMESTRING", kind="stable"),
                           left_on="mid_elapsed", right_on="PCTIMESTRING",
                           left_by="game_id", right_by="GAME_ID",
                           direction="backward")

    # sanity: the focal player must be in the matched lineup on his side
    own_cols = np.where(merged["side"] == "HOME", "H", "A")
    own = np.zeros(len(merged), dtype=bool)
    for i, cols in ((0, HOME_COLS), (1, AWAY_COLS)):
        block = merged[cols].to_numpy()
        hit = (block == merged["player_id"].to_numpy()[:, None]).any(axis=1)
        own |= hit & (own_cols == ("H" if i == 0 else "A"))
    match_rate = own.mean()

    rapm = pd.read_csv(VALUE_DIR / f"rapm_{EVAL_SEASON}.csv").set_index("player_id")["rapm"]
    opp_cols = [merged[AWAY_COLS], merged[HOME_COLS]]
    opp_block = np.where((merged["side"] == "HOME").to_numpy()[:, None],
                         opp_cols[0].to_numpy(), opp_cols[1].to_numpy())
    opp_rapm48 = (pd.DataFrame(opp_block).apply(lambda c: c.map(rapm)).fillna(0.0)
                  .sum(axis=1) * 48)
    merged["opp_rapm48"] = opp_rapm48.to_numpy()
    return merged, match_rate


def tercile_table(occ: pd.DataFrame, col: str) -> pd.DataFrame:
    occ = occ.copy()
    occ["tercile"] = pd.qcut(occ[col], 3, labels=TERCILE_LABELS)
    tbl = occ.groupby("tercile", observed=True).agg(
        occurrences=("cost_wp", "count"),
        mean_pp_est=("cost_wp", "mean"),
        mean_pp_k0=("cost_wp_k0", "mean"),
        split_lo=(col, "min"), split_hi=(col, "max"))
    tbl["mean_pp_est"] *= 100
    tbl["mean_pp_k0"] *= 100
    return tbl.loc[["strong", "average", "weak"]]


def run() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    support, probs, mean_step = margin_step_distribution()
    kappa = pd.read_csv(HAZARD_DIR / "kappa.csv", index_col=0).loc["foul_trouble", "coef"]
    occ = occurrence_frame(
        evaluate_convention_cost(support, probs, mean_step, kappa),
        evaluate_convention_cost(support, probs, mean_step, 0.0))

    ts = team_season_net_ratings()
    net = ts[ts["season"] == EVAL_SEASON].set_index("team")["net100"]
    occ["opp_net100"] = occ["opponent"].map(net)
    a = tercile_table(occ, "opp_net100")

    occ_b, match_rate = opponent_lineup_rapm(occ)
    b = tercile_table(occ_b, "opp_rapm48")

    passed = bool((a["mean_pp_k0"] > 0).all())
    lines = [
        f"# E8 — opponent-strength robustness split ({EVAL_SEASON}, "
        f"{len(occ):,} occurrences)", "",
        "## Panel A (primary): opponent team-season net rating terciles",
        "Net rating = points scored minus allowed per 100 possessions at the",
        "league-pace possession convention (100/48 per minute, identical to",
        "net points per 48), computed from final scores and game minutes in",
        "the behavioral-window play-by-play.", "",
        a.round(2).to_string(), "",
        f"PASS CONDITION (pre-registered): mean cost per occurrence positive "
        f"in every Panel A tercile at kappa = 0 -> "
        f"{'PASS' if passed else 'FAIL'}", "",
        "## Panel B (secondary): opponent on-floor lineup RAPM terciles",
        f"Summed RAPM of the five opponent players on the floor at the",
        f"decision moment (mid-spell lineup; focal-player-in-lineup match "
        f"rate {match_rate:.1%}), {EVAL_SEASON} ratings, burn-in rules "
        f"unchanged.", "",
        b.round(2).to_string(), "",
        "Note: the Panel B split correlates with score state (weak lineups",
        "appear in blowouts, when starters rest), so Panel A is the primary",
        "evidence; Panel B is corroboration only.", "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    def rows(t):
        return {lab: {"n": int(t.loc[lab, "occurrences"]),
                      "est": round(float(t.loc[lab, "mean_pp_est"]), 3),
                      "k0": round(float(t.loc[lab, "mean_pp_k0"]), 3)}
                for lab in TERCILE_LABELS}
    OUT_META.write_text(json.dumps({
        "n_occurrences": len(occ), "passed": passed,
        "match_rate": round(float(match_rate), 4),
        "panel_a": rows(a), "panel_b": rows(b),
    }, indent=1))
    print("\n".join(lines))
    print(f"wrote {OUT_MD} and {OUT_META}")


if __name__ == "__main__":
    run()
