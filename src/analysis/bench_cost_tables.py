"""Per-player and per-team WP cost of the Q+1 convention (E6/E7 artifacts).

V_opt - V_conv at the first observed foul-trouble state per player-game in
EVAL_SEASON (solver Section 3.5 machinery), evaluated at estimated kappa and
at kappa = 0. kappa_share = fraction of a player's season-total cost
attributable to the kappa boost; high-share rows are provisional on the B0
selection check (reports/kappa_b0.md).

Occurrences carry the team they happened for, so traded players split
across their teams without double-counting.

Outputs:
  data/processed/analysis/bench_cost_per_player.csv
  data/processed/analysis/bench_cost_per_team.csv
"""

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from config import EVAL_SEASON  # noqa: E402
from policy.solver import margin_step_distribution, evaluate_convention_cost  # noqa: E402

HAZARD_DIR = ROOT / "data" / "processed" / "hazard"
VALUE_DIR = ROOT / "data" / "processed" / "value"
OUT_DIR = ROOT / "data" / "processed" / "analysis"
MIN_OCC = 5  # ranking floor; the CSV keeps everyone evaluated


def run() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    support, probs, mean_step = margin_step_distribution()
    kappa = pd.read_csv(HAZARD_DIR / "kappa.csv", index_col=0).loc["foul_trouble", "coef"]
    est = evaluate_convention_cost(support, probs, mean_step, kappa)
    k0 = evaluate_convention_cost(support, probs, mean_step, 0.0)

    deltas = pd.read_csv(VALUE_DIR / f"delta_{EVAL_SEASON}.csv").set_index("player_id")
    per = est.groupby("player_id")["cost_wp"].agg(["mean", "sum", "count"])
    per["mean_pp"] = per["mean"] * 100
    per["total_pp"] = per["sum"] * 100
    per["total_pp_k0"] = k0.groupby("player_id")["cost_wp"].sum() * 100
    per["kappa_share"] = ((per["total_pp"] - per["total_pp_k0"])
                          / per["total_pp"]).where(per["total_pp"] > 0)
    per["name"] = per.index.map(deltas["name"])
    per["delta48"] = per.index.map(deltas["delta"]) * 48
    cols = ["name", "mean_pp", "total_pp", "total_pp_k0", "kappa_share",
            "count", "delta48"]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    per[cols].to_csv(OUT_DIR / "bench_cost_per_player.csv")

    team = est.groupby("team")["cost_wp"].agg(wins_est="sum", occurrences="count")
    team["wins_k0"] = k0.groupby("team")["cost_wp"].sum()
    team = team.sort_values("wins_est", ascending=False)
    team.to_csv(OUT_DIR / "bench_cost_per_team.csv")

    ranked = per[per["count"] >= MIN_OCC]
    print(f"{EVAL_SEASON}: {len(per)} players evaluated, "
          f"{len(ranked)} with >= {MIN_OCC} occurrences\n")
    for label, col in (("per occurrence (mean_pp)", "mean_pp"),
                       ("season total (total_pp)", "total_pp")):
        print(f"TOP 20 by {label}:")
        print(ranked.nlargest(20, col)[cols].round(2).to_string(index=False))
        print(f"\nBOTTOM 20 by {label}:")
        print(ranked.nsmallest(20, col)[cols].round(2).to_string(index=False))
        print()
    print("teams ranked by wins lost per season to the convention:")
    print(team.round(2).to_string())
    print(f"\nwrote {OUT_DIR / 'bench_cost_per_player.csv'} and "
          f"{OUT_DIR / 'bench_cost_per_team.csv'}")


if __name__ == "__main__":
    run()
