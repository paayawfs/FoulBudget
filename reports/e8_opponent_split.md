# E8 — opponent-strength robustness split (2025, 2,485 occurrences)

## Panel A (primary): opponent team-season net rating terciles
Net rating = points scored minus allowed per 100 possessions at the
league-pace possession convention (100/48 per minute, identical to
net points per 48), computed from final scores and game minutes in
the behavioral-window play-by-play.

         occurrences  mean_pp_est  mean_pp_k0  split_lo  split_hi
tercile                                                          
strong           749         1.90        0.34      4.81     11.05
average          871         1.92        0.34     -0.18      4.11
weak             865         1.94        0.34    -11.94     -0.29

PASS CONDITION (pre-registered): mean cost per occurrence positive in every Panel A tercile at kappa = 0 -> PASS

## Panel B (secondary): opponent on-floor lineup RAPM terciles
Summed RAPM of the five opponent players on the floor at the
decision moment (mid-spell lineup; focal-player-in-lineup match rate 100.0%), 2025 ratings, burn-in rules unchanged.

         occurrences  mean_pp_est  mean_pp_k0  split_lo  split_hi
tercile                                                          
strong           828         1.95        0.37      7.87     24.70
average          828         1.93        0.34      1.87      7.87
weak             829         1.88        0.32    -17.23      1.86

Note: the Panel B split correlates with score state (weak lineups
appear in blowouts, when starters rest), so Panel A is the primary
evidence; Panel B is corroboration only.
