# E8 — opponent-strength robustness split (2025, 2,423 occurrences)

## Panel A (primary): opponent team-season net rating terciles
Net rating = points scored minus allowed per 100 possessions at the
league-pace possession convention (100/48 per minute, identical to
net points per 48), computed from final scores and game minutes in
the behavioral-window play-by-play.

         occurrences  mean_pp_est  mean_pp_k0  split_lo  split_hi
tercile                                                          
strong           808         2.52        0.79      4.11     11.05
average          769         2.53        0.81     -0.18      3.34
weak             846         2.56        0.80    -11.94     -0.29

PASS CONDITION (pre-registered): mean cost per occurrence positive in every Panel A tercile at kappa = 0 -> PASS

## Panel B (secondary): opponent on-floor lineup RAPM terciles
Summed RAPM of the five opponent players on the floor at the
decision moment (mid-spell lineup; focal-player-in-lineup match rate 100.0%), 2025 ratings, burn-in rules unchanged.

         occurrences  mean_pp_est  mean_pp_k0  split_lo  split_hi
tercile                                                          
strong           808         2.54        0.76      7.79     24.70
average          807         2.57        0.83      1.73      7.76
weak             808         2.50        0.80    -17.23      1.73

Note: the Panel B split correlates with score state (weak lineups
appear in blowouts, when starters rest), so Panel A is the primary
evidence; Panel B is corroboration only.
