# kappa v2 — per-player deviations, ridge partial pooling (5 seasons: 2021–2025)

deviation columns: 795 players | lambda_kappa = 640 (2-fold CV over games)
kappa-bar (global): +4.33 per 48
reconciliation: v1 pooled kappa +4.22 per 48; FT-minutes-weighted mean kappa_i +4.22 per 48

## OOS gate (held-out FT spells, minutes-weighted MSE)
pooled kappa-bar: 7.336267 | with kappa_i: 7.334002 | gain +0.002265 (+0.031%)

## C3 — shrinkage vs exposure (dev_per48 by pooled FT possessions)
                  n    sd  max_abs
ft_poss                           
[0.0, 25.0)     257  0.44     1.51
[25.0, 50.0)    124  0.69     2.00
[50.0, 100.0)   138  1.10     2.98
[100.0, 250.0)  193  1.53     4.24
[250.0, 500.0)   67  1.97     5.10
[500.0, inf)     16  2.80     6.77

## face validity — reportable players (>= 250 FT poss, n = 83)
most negative kappa_i (per 48):
          name  ft_poss  kappa_per48
   P. Banchero    323.5        -0.78
  B. Coulibaly    351.3        -0.74
J. Jackson Jr.    830.8        -0.20
     D. Powell    328.5         0.57
    D. Gafford    460.0         0.71
least negative / most positive:
         name  ft_poss  kappa_per48
  N. Richards    287.7         6.85
     T. Maxey    288.7         7.82
   D. Sabonis    772.6         7.93
Fred VanVleet    407.0         8.06
     J. Suggs    591.4        11.10