"""B0 selection check per HIERARCHICAL_KAPPA_PLAN.md Phase B0 — widened
rerun per the pre-registered protocol in reports/kappa_b0.md (2026-07-24).

Splits foul-trouble exposure into FORCED (late, close, high-delta player --
benching is not a live option), EXCLUDED-final90 (the take-foul/FT-contest
window: spell starts in the final 90 seconds of regulation/OT while within
one possession, |d| <= 3 — its own regression cell so it contaminates
neither side), and CHOSEN (everything else). Pooled kappa-bar estimated on
each with the same spell WLS as v1/v2. The DiD spec adds the window main
effect (clutch indicator for ALL spells in the window), so
foul_trouble[FORCED] reads as the within-clutch foul-trouble shift net of
the general clutch intensity effect -- the verdict number.

Rung ladder (pre-registered, stopping rule enforced in code):
  rung 1: final 7.0 min, |d| <= 6, top-half delta, final-90s exclusion
  rung 2: final 9.0 min, same margin/exclusion — ONLY if rung 1 is
          ambiguous (positive but t < 2 in the DiD spec)
  after rung 2 the result stands as-is; ambiguous after rung 2 =
  "underpowered, not contradicted" permanently.

Spells are classified by their START state (a spell straddling the window
boundary counts where it starts). Fixed 2026-07-26: foul trouble in OT used
to be structurally unreachable (trouble in period p >= 5 needed p+1 >= 6
fouls, i.e. disqualification) so FORCED foul-trouble mass was entirely
late-Q4 five-foul spells; config.foul_trouble_threshold now caps the OT
threshold at 5 fouls, so OT foul-trouble spells (a player at 5 fouls
playing on into overtime) now contribute FORCED exposure too, on top of
already feeding the window main effect.

Appends the results section to reports/kappa_b0.md (pre-registration and
prior-run text above the marker are preserved) and writes
data/processed/hazard/kappa_b0_meta.json (consumed by
tests/run_validation.py for the B0 summary row).
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
OT_SEC = 300

ROTATION_MIN_MINUTES = 500   # rotation floor for the delta split
EXCL_SEC = 90                # take-foul/FT-contest window (contamination check)
EXCL_MARGIN = 3              # ... within one possession
# pre-registered rung ladder: (window_sec, margin); rung 2 only if rung 1
# is ambiguous with a positive point estimate. No rung 3, ever.
RUNGS = ((420.0, 6), (540.0, 6))

RESULTS_MARKER = "<!-- widened-results -->"


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


def final90_mask(df: pd.DataFrame) -> pd.Series:
    """Exact exclusion definition from the endgame-ritual contamination
    check: spell starts in the final EXCL_SEC of regulation/OT while within
    one possession."""
    period_end = np.where(df["period"] >= 5,
                          REGULATION_SEC + (df["period"] - 4) * OT_SEC,
                          REGULATION_SEC)
    in_final = (period_end - df["start_elapsed"]) <= EXCL_SEC
    return in_final & (df["score_margin"].abs() <= EXCL_MARGIN)


def coef_rows(res: pd.DataFrame, names) -> pd.DataFrame:
    out = res.loc[list(names)].copy()
    out["per48"] = out["coef"] * 48
    out["se48"] = out["se"] * 48
    out["t"] = out["coef"] / out["se"]
    return out[["per48", "se48", "t"]]


def run_rung(df: pd.DataFrame, ft: pd.Series, window_sec: float, margin: int):
    W = window_mask(df, window_sec, margin)
    excl = W & final90_mask(df)
    tier = pd.Series(np.where(excl, "EXCLUDED-final90",
                     np.where(W, "FORCED", "CHOSEN")), index=df.index)

    poss = {v: df.loc[ft & (tier == v), "minutes_exposed"].sum() * POSS_PER_MIN
            for v in ("FORCED", "EXCLUDED-final90", "CHOSEN")}
    n_spells = int((ft & (tier == "FORCED")).sum())

    names = ["foul_trouble[FORCED]", "foul_trouble[EXCLUDED-final90]",
             "foul_trouble[CHOSEN]"]
    raw = fit(df, tier=tier)
    did = fit(df, tier=tier,
              extra_covs=pd.DataFrame({"clutch_window": W.astype(float).to_numpy()}))

    lines = [f"### Rung {'1' if window_sec == RUNGS[0][0] else '2'}: "
             f"final {window_sec / 60:g} min, |d| <= {margin}, top-half delta, "
             f"final-{EXCL_SEC}s one-possession spells excluded"]
    lines.append(f"FORCED: {poss['FORCED']:,.0f} poss ({n_spells:,} spells) | "
                 f"EXCLUDED-final90: {poss['EXCLUDED-final90']:,.0f} poss | "
                 f"CHOSEN: {poss['CHOSEN']:,.0f} poss")
    lines.append("")

    kf, kc = raw.loc["foul_trouble[FORCED]"], raw.loc["foul_trouble[CHOSEN]"]
    diff_t = (kf["coef"] - kc["coef"]) / np.hypot(kf["se"], kc["se"])
    lines.append("raw split (per 48; naive SEs, difference t ignores covariance):")
    lines.append(coef_rows(raw, names).round(2).to_string())
    lines.append(f"difference FORCED - CHOSEN: "
                 f"{(kf['coef'] - kc['coef']) * 48:+.2f} per 48, t = {diff_t:.2f}")
    lines.append("")

    df_, dc_ = did.loc["foul_trouble[FORCED]"], did.loc["foul_trouble[CHOSEN]"]
    did_diff_t = (df_["coef"] - dc_["coef"]) / np.hypot(df_["se"], dc_["se"])
    lines.append("DiD spec (window main effect included; foul_trouble[FORCED] "
                 "= within-clutch foul-trouble shift — the verdict number):")
    lines.append(coef_rows(did, names + ["clutch_window"]).round(2).to_string())
    lines.append(f"DiD difference FORCED - CHOSEN: "
                 f"{(df_['coef'] - dc_['coef']) * 48:+.2f} per 48, t = {did_diff_t:.2f}")
    lines.append("")

    t_did = df_["coef"] / df_["se"]
    if df_["coef"] <= 0:
        verdict = "selection-driven"
    elif t_did >= 2:
        verdict = "defended"
    else:
        verdict = "ambiguous"

    ke = did.loc["foul_trouble[EXCLUDED-final90]"]
    meta = {
        "window_sec": window_sec, "margin": margin,
        "forced_poss": round(poss["FORCED"]),
        "excl_poss": round(poss["EXCLUDED-final90"]),
        "chosen_poss": round(poss["CHOSEN"]),
        "raw_forced_per48": kf["coef"] * 48, "raw_forced_t": kf["coef"] / kf["se"],
        "raw_chosen_per48": kc["coef"] * 48,
        "did_forced_per48": df_["coef"] * 48, "did_forced_t": t_did,
        "did_chosen_per48": dc_["coef"] * 48, "did_diff_t": did_diff_t,
        "excl_per48": ke["coef"] * 48, "excl_t": ke["coef"] / ke["se"],
    }
    return verdict, lines, meta


def run() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    df = load()
    df["top_half"] = top_half_flags(df)
    ft = df["foul_trouble"] == 1

    all_lines = [RESULTS_MARKER, "", "## Widened rerun — results "
                 "(protocol above, registered before running)", ""]
    for rung_idx, (window_sec, margin) in enumerate(RUNGS, start=1):
        verdict, lines, meta = run_rung(df, ft, window_sec, margin)
        all_lines += lines
        if rung_idx == 1 and not (verdict == "ambiguous"
                                  and meta["did_forced_per48"] > 0):
            break  # stopping rule: rung 2 only on ambiguous-but-positive
    meta["rung"] = rung_idx
    meta["verdict"] = verdict

    if verdict == "defended":
        vtext = ("VERDICT (pre-registered threshold): DEFENDED — FORCED-core "
                 "kappa-bar positive with t >= 2 in the DiD spec. Adaptation "
                 "survives where the coach has no real choice; the "
                 "estimated-kappa headline may cite B0 as its identification "
                 "defense.")
    elif verdict == "selection-driven":
        vtext = ("VERDICT (pre-registered threshold): SELECTION-DRIVEN — "
                 "FORCED-core point estimate at or below zero. The positive "
                 "pooled kappa is substantially selection; the kappa-boosted "
                 "numbers are not causally defensible. Downstream artifacts "
                 "flagged: headline table, E6 per-player tables, E7 team "
                 "slice, kappa_share column.")
    elif rung_idx == 2:
        vtext = ("VERDICT (pre-registered threshold, after rung 2): "
                 "UNDERPOWERED, NOT CONTRADICTED — permanent per the "
                 "stopping rule. FORCED-core kappa-bar is positive but "
                 "t < 2. REFERENCE.md keeps the 'kappa is an upper bound on "
                 "the causal effect' posture; the abstract leads with the "
                 "0.65 floor.")
    else:
        vtext = ("VERDICT (pre-registered threshold): AMBIGUOUS at rung 1 "
                 "with a non-positive trigger state — rung 2 not run.")
    all_lines += [vtext, ""]

    text = OUT_MD.read_text(encoding="utf-8")
    if RESULTS_MARKER in text:  # idempotent: replace prior results section
        text = text.split(RESULTS_MARKER, 1)[0].rstrip() + "\n"
    OUT_MD.write_text(text + "\n" + "\n".join(all_lines), encoding="utf-8")
    (HAZARD_DIR / "kappa_b0_meta.json").write_text(json.dumps(meta, indent=1))
    print("\n".join(all_lines))
    print(f"\nwrote {OUT_MD} and {HAZARD_DIR / 'kappa_b0_meta.json'}")


if __name__ == "__main__":
    run()
