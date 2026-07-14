"""Phase A feasibility audit per HIERARCHICAL_KAPPA_PLAN.md.

Tabulates foul-trouble exposure per player (the binding constraint for
per-player kappa_i), and estimates pooled kappa-bar by candidate grouping
variables (foul-rate tier, minutes tier) so the coarsest meaningful grouping
can be chosen. Positions are not in the play-by-play, so that candidate
waits for a roster join.

Possessions are approximated as minutes x 100/48 (league pace); the exposure
table is minute-denominated. Run on the current dev slice this audit shows
what 3 seasons support; rerun after data expansion for the Phase A decision
proper.

Writes reports/kappa_audit.md.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from hazard.kappa import load, fit  # noqa: E402

OUT = Path(__file__).resolve().parents[2] / "reports" / "kappa_audit.md"
POSS_PER_MIN = 100 / 48
THRESHOLDS = (100, 250, 500)


def text_hist(values, edges) -> str:
    counts, _ = np.histogram(values, bins=edges)
    peak = counts.max()
    lines = []
    for i, c in enumerate(counts):
        bar = "#" * max(1, round(c / peak * 40)) if c else ""
        lines.append(f"  {edges[i]:>5.0f}-{edges[i + 1]:>5.0f}: {c:>4} {bar}")
    return "\n".join(lines)


def run() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    df = load()
    ft = df[df["foul_trouble"] == 1]

    per_ps = ft.groupby(["player_id", "season"])["minutes_exposed"].sum() * POSS_PER_MIN
    pooled = per_ps.groupby("player_id").sum()

    lines = ["# Phase A feasibility audit — foul-trouble exposure (dev slice, 3 seasons)", ""]
    lines.append(f"players with ANY foul-trouble time: {len(pooled)}")
    lines.append(f"total foul-trouble possessions (approx): {pooled.sum():,.0f}")
    lines.append("")
    q = per_ps.quantile([0.1, 0.25, 0.5, 0.75, 0.9]).round(1)
    lines.append("## per player-SEASON foul-trouble possessions (quantiles)")
    lines.append(q.to_string())
    lines.append("")
    qp = pooled.quantile([0.1, 0.25, 0.5, 0.75, 0.9]).round(1)
    lines.append("## per player POOLED across 3 seasons (quantiles)")
    lines.append(qp.to_string())
    lines.append("")
    lines.append("## players above candidate thresholds (pooled possessions)")
    for th in THRESHOLDS:
        lines.append(f"  >= {th}: {(pooled >= th).sum()}")
    lines.append("")
    lines.append("## histogram, pooled possessions per player")
    lines.append("```")
    base_edges = [0, 25, 50, 100, 150, 250, 400, 600, 1000]
    edges = np.array([e for e in base_edges if e < pooled.max()] + [pooled.max() + 1])
    lines.append(text_hist(pooled, edges))
    lines.append("```")
    lines.append("")

    # state coverage of foul-trouble exposure
    cov = ft.groupby("period")["minutes_exposed"].sum()
    lines.append("## state coverage: foul-trouble minutes by period")
    lines.append((cov / cov.sum() * 100).round(1).to_string())
    lines.append(f"mean |margin| in trouble: {ft['abs_margin'].mean():.1f} "
                 f"(vs {df['abs_margin'].mean():.1f} overall)")
    lines.append("")

    # grouping candidates: pooled kappa-bar per tier
    total_min = df.groupby("player_id")["minutes_exposed"].sum()
    fouls = df.groupby("player_id")["fouls_in_window"].sum()
    per36 = (fouls / total_min * 36).reindex(df["player_id"]).values
    minutes_pl = total_min.reindex(df["player_id"]).values
    foul_tier = pd.Series(pd.qcut(per36, 3, labels=["low-foul", "mid-foul", "high-foul"]),
                          index=df.index)
    min_tier = pd.Series(pd.qcut(minutes_pl, 3, labels=["low-min", "mid-min", "high-min"]),
                         index=df.index)

    for label, tier in (("foul-rate tier", foul_tier), ("minutes tier", min_tier)):
        res = fit(df, tier=tier)
        res = res[res.index.str.startswith("foul_trouble")]
        res["per48"] = res["coef"] * 48
        res["t"] = res["coef"] / res["se"]
        lines.append(f"## pooled kappa-bar by {label} (pts/48, minutes-weighted WLS)")
        lines.append(res[["per48", "t"]].round(2).to_string())
        lines.append("")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    run()
