"""B0 selection check per HIERARCHICAL_KAPPA_PLAN.md Phase B0.

Splits foul-trouble exposure into FORCED (late, close, high-delta player --
benching is not a live option) and CHOSEN (everything else), estimates pooled
kappa-bar on each with the same spell WLS as v1/v2, and reports the
difference. The DiD spec adds the window main effect (clutch indicator for
ALL spells), so foul_trouble[FORCED] reads as the within-clutch foul-trouble
shift net of the general clutch intensity effect -- the cleaner number.

Spells are classified by their START state (a spell straddling the window
boundary counts where it starts); exposure spells at 5 fouls are short, so
the misclassified mass is small. Under Q+1, OT contributes no foul-trouble
exposure (trouble in period p needs p+1 >= 6 fouls), so FORCED foul-trouble
mass is late-Q4 five-foul spells; OT still feeds the window main effect.

Writes reports/kappa_b0.md and data/processed/hazard/kappa_b0_meta.json
(consumed by tests/run_validation.py for the B0 summary row).
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import ANALYSIS_SEASONS  # noqa: E402
from hazard.kappa import load, fit  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
VALUE_DIR = ROOT / "data" / "processed" / "value"
HAZARD_DIR = ROOT / "data" / "processed" / "hazard"
OUT_MD = ROOT / "reports" / "kappa_b0.md"
POSS_PER_MIN = 100 / 48
REGULATION_SEC = 2880

FORCED_WINDOW_SEC = 300.0    # final 5.0 minutes of regulation
FORCED_MARGIN = 3            # one possession
ROTATION_MIN_MINUTES = 500   # rotation floor for the delta split
MIN_FORCED_POSS = 2000       # widen the window below this
MIN_TIER_CELL_POSS = 500     # tier-split cells need at least this
ENDGAME_EXCLUDE_SEC = 90     # robustness: strip the intentional-fouling window
OT_SEC = 300
# widening ladder per the plan: margin first, then the time window
LADDER = ((FORCED_WINDOW_SEC, FORCED_MARGIN),
          (FORCED_WINDOW_SEC, 6),
          (420.0, 6))

INTERPRETATION = """\
Decision rule (logged verbatim per HIERARCHICAL_KAPPA_PLAN Phase B0, no
thumb on the scale):
- If FORCED kappa-bar remains significantly positive: adaptation is real;
  the estimated-kappa headline (2.05 wins) stands with this as its
  identification defense.
- If FORCED kappa-bar is ~0 or negative: the positive pooled kappa is
  substantially selection; the defensible headline shifts toward the
  kappa=0 floor (0.65 wins), and paper language must change. Flag every
  downstream artifact this touches (headline table, per-player cost
  tables, top-20 lists).

Known confound either way: FORCED minutes are high-leverage end-game
minutes, so intensity/effort differs from average minutes independent of
foul trouble. The DiD spec (window main effect included; the
foul_trouble[FORCED] coefficient is then the within-clutch foul-trouble
shift) mitigates this and is the cleaner number."""


def top_half_flags(df: pd.DataFrame) -> pd.Series:
    """True where the spell's player-season delta48 is in the top half of
    rotation players (>= ROTATION_MIN_MINUTES) for that season."""
    frames = []
    for s in ANALYSIS_SEASONS:
        d = pd.read_csv(VALUE_DIR / f"delta_{s}.csv").dropna(subset=["delta"])
        d = d[d["minutes"] >= ROTATION_MIN_MINUTES]
        top = d[d["delta"] >= d["delta"].median()]
        frames.append(pd.DataFrame({"player_id": top["player_id"], "season": s,
                                    "top_half": True}))
    flags = pd.concat(frames, ignore_index=True)
    merged = df[["player_id", "season"]].merge(flags, how="left",
                                               on=["player_id", "season"])
    return merged["top_half"].notna().set_axis(df.index)


def window_mask(df: pd.DataFrame, window_sec: float, margin: int) -> pd.Series:
    clutch_time = (
        ((df["period"] == 4) & (REGULATION_SEC - df["start_elapsed"] <= window_sec))
        | (df["period"] >= 5)
    )
    return clutch_time & (df["score_margin"].abs() <= margin) & df["top_half"]


def coef_rows(res: pd.DataFrame, names) -> pd.DataFrame:
    out = res.loc[list(names)].copy()
    out["per48"] = out["coef"] * 48
    out["se48"] = out["se"] * 48
    out["t"] = out["coef"] / out["se"]
    return out[["per48", "se48", "t"]]


def run() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    df = load()
    df["top_half"] = top_half_flags(df)
    ft = df["foul_trouble"] == 1

    widenings = []
    for window_sec, margin in LADDER:
        W = window_mask(df, window_sec, margin)
        forced_poss = df.loc[ft & W, "minutes_exposed"].sum() * POSS_PER_MIN
        widenings.append(f"window {window_sec / 60:g} min, |d| <= {margin}: "
                         f"{forced_poss:,.0f} FORCED foul-trouble possessions")
        if forced_poss >= MIN_FORCED_POSS:
            break
    chosen_poss = df.loc[ft & ~W, "minutes_exposed"].sum() * POSS_PER_MIN
    n_forced_spells = int((ft & W).sum())

    lines = [f"# B0 selection check — FORCED vs CHOSEN foul-trouble exposure "
             f"({len(ANALYSIS_SEASONS)} seasons: {ANALYSIS_SEASONS[0]}–{ANALYSIS_SEASONS[-1]})", ""]
    lines.append("## Subsample sizes (report these before anything else)")
    for msg in widenings:
        lines.append(f"- {msg}")
    lines.append(f"- final window: last {window_sec / 60:g} min of regulation "
                 f"(or OT), |d| <= {margin}, top-half delta48 among rotation "
                 f"players (>= {ROTATION_MIN_MINUTES} min)")
    lines.append(f"- FORCED: {forced_poss:,.0f} possessions ({n_forced_spells:,} spells) | "
                 f"CHOSEN: {chosen_poss:,.0f} possessions")
    lines.append("")

    tier = pd.Series(np.where(W, "FORCED", "CHOSEN"), index=df.index)
    raw = fit(df, tier=tier)
    did = fit(df, tier=tier,
              extra_covs=pd.DataFrame({"clutch_window": W.astype(float).to_numpy()}))

    raw_tbl = coef_rows(raw, ["foul_trouble[FORCED]", "foul_trouble[CHOSEN]"])
    kf, kc = raw.loc["foul_trouble[FORCED]"], raw.loc["foul_trouble[CHOSEN]"]
    diff = (kf["coef"] - kc["coef"]) * 48
    diff_t = (kf["coef"] - kc["coef"]) / np.hypot(kf["se"], kc["se"])
    lines.append("## Raw split (per 48; naive SEs, difference t ignores covariance)")
    lines.append(raw_tbl.round(2).to_string())
    lines.append(f"difference FORCED - CHOSEN: {diff:+.2f} per 48, t = {diff_t:.2f}")
    lines.append("")

    did_tbl = coef_rows(did, ["foul_trouble[FORCED]", "foul_trouble[CHOSEN]",
                              "clutch_window"])
    df_, dc_ = did.loc["foul_trouble[FORCED]"], did.loc["foul_trouble[CHOSEN]"]
    did_diff_t = (df_["coef"] - dc_["coef"]) / np.hypot(df_["se"], dc_["se"])
    lines.append("## DiD spec (window main effect included; foul_trouble[FORCED]")
    lines.append("## = within-clutch foul-trouble shift — the cleaner number)")
    lines.append(did_tbl.round(2).to_string())
    lines.append(f"DiD difference FORCED - CHOSEN: "
                 f"{(df_['coef'] - dc_['coef']) * 48:+.2f} per 48, t = {did_diff_t:.2f}")
    lines.append("")

    # endgame-ritual robustness: the final ~90s of close games hold take
    # fouls, FT contests, and trailing-team gambles that inflate scoring
    # independent of adaptation. FORCED-core (window minus final 90s) must
    # stay positive on its own.
    period_end = np.where(df["period"] >= 5,
                          REGULATION_SEC + (df["period"] - 4) * OT_SEC,
                          REGULATION_SEC)
    in_final = (period_end - df["start_elapsed"]) <= ENDGAME_EXCLUDE_SEC
    tier3 = pd.Series(np.where(W & in_final, "FORCED-final90",
                      np.where(W, "FORCED-core", "CHOSEN")), index=df.index)
    core_poss = df.loc[ft & (tier3 == "FORCED-core"), "minutes_exposed"].sum() * POSS_PER_MIN
    fin_poss = df.loc[ft & (tier3 == "FORCED-final90"), "minutes_exposed"].sum() * POSS_PER_MIN
    rob = fit(df, tier=tier3,
              extra_covs=pd.DataFrame({"clutch_window": W.astype(float).to_numpy()}))
    rob_tbl = coef_rows(rob, ["foul_trouble[FORCED-core]",
                              "foul_trouble[FORCED-final90]",
                              "foul_trouble[CHOSEN]", "clutch_window"])
    rc = rob.loc["foul_trouble[FORCED-core]"]
    lines.append(f"## Endgame-ritual robustness (final {ENDGAME_EXCLUDE_SEC}s "
                 f"split out; DiD spec)")
    lines.append(f"FORCED-core: {core_poss:,.0f} poss | "
                 f"FORCED-final90: {fin_poss:,.0f} poss")
    lines.append(rob_tbl.round(2).to_string())
    lines.append("")

    # tier-level split if every FORCED cell holds enough exposure
    total_min = df.groupby("player_id")["minutes_exposed"].sum()
    fouls = df.groupby("player_id")["fouls_in_window"].sum()
    per36 = (fouls / total_min * 36).reindex(df["player_id"]).values
    foul_tier = pd.Series(pd.qcut(per36, 3, labels=["low-foul", "mid-foul", "high-foul"]),
                          index=df.index).astype(str)
    cross = tier + "|" + foul_tier
    cell_poss = (df.loc[ft, "minutes_exposed"].groupby(cross[ft]).sum() * POSS_PER_MIN)
    lines.append("## Foul-rate tier x FORCED/CHOSEN cell sizes (possessions)")
    lines.append(cell_poss.round(0).to_string())
    forced_cells = cell_poss[cell_poss.index.str.startswith("FORCED")]
    if forced_cells.min() >= MIN_TIER_CELL_POSS:
        res_t = fit(df, tier=cross)
        tbl = coef_rows(res_t, [i for i in res_t.index if i.startswith("foul_trouble")])
        lines.append("")
        lines.append("## Tier-level split (per 48)")
        lines.append(tbl.round(2).to_string())
    else:
        lines.append(f"tier split SKIPPED: smallest FORCED cell "
                     f"{forced_cells.min():,.0f} < {MIN_TIER_CELL_POSS} possessions")
    lines.append("")

    lines.append("## Interpretation")
    lines.append(INTERPRETATION)
    lines.append("")

    # verdict per the decision rule, on the raw FORCED estimate, cross-checked
    # against the DiD and the endgame-ritual robustness spec; qualitative
    # disagreement -> ambiguous, stop and report
    raw_pos = kf["coef"] / kf["se"] >= 2
    did_pos = (df_["coef"] / df_["se"] >= 2) and (rc["coef"] / rc["se"] >= 2)
    raw_zero = kf["coef"] * 48 <= 1.0  # ~0 or negative on the per-48 scale
    did_zero = df_["coef"] * 48 <= 1.0
    if raw_pos and did_pos:
        verdict = "stands"
        vtext = ("VERDICT: FORCED kappa-bar significantly positive in both "
                 "specs — adaptation is real; the estimated-kappa headline "
                 "stands with B0 as its identification defense.")
    elif raw_zero and did_zero:
        verdict = "selection"
        vtext = ("VERDICT: FORCED kappa-bar ~0/negative in both specs — the "
                 "pooled kappa is substantially selection; the defensible "
                 "headline shifts toward the kappa=0 floor (0.65 wins). "
                 "FLAGGED downstream artifacts: headline table "
                 "(VALIDATION.md re-estimation section), per-player cost "
                 "tables and top-20 lists (E6), team slice (E7), threshold "
                 "maps at estimated kappa.")
    else:
        verdict = "ambiguous"
        vtext = ("VERDICT: AMBIGUOUS — the raw and DiD specs do not agree "
                 "(or FORCED kappa-bar is positive but not significant). "
                 "Stop and review before changing any paper language.")
    lines.append(vtext)

    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    (HAZARD_DIR / "kappa_b0_meta.json").write_text(json.dumps({
        "window_sec": window_sec, "margin": margin,
        "forced_poss": round(forced_poss), "chosen_poss": round(chosen_poss),
        "widenings": len(widenings) - 1,
        "raw_forced_per48": kf["coef"] * 48, "raw_forced_t": kf["coef"] / kf["se"],
        "raw_chosen_per48": kc["coef"] * 48, "raw_diff_t": diff_t,
        "did_forced_per48": df_["coef"] * 48, "did_forced_t": df_["coef"] / df_["se"],
        "did_chosen_per48": dc_["coef"] * 48, "did_diff_t": did_diff_t,
        "core_per48": rc["coef"] * 48, "core_t": rc["coef"] / rc["se"],
        "core_poss": round(core_poss),
        "verdict": verdict,
    }, indent=1))
    print("\n".join(lines))
    print(f"\nwrote {OUT_MD} and {HAZARD_DIR / 'kappa_b0_meta.json'}")


if __name__ == "__main__":
    run()
