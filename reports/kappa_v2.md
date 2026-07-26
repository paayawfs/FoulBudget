# kappa v2 — per-player deviations, ridge partial pooling (5 seasons: 2021–2025)

deviation columns: 798 players | lambda_kappa = 640 (2-fold CV over games)
kappa-bar (global): +4.12 per 48
reconciliation: v1 pooled kappa +3.98 per 48; FT-minutes-weighted mean kappa_i +3.98 per 48

## OOS gate (held-out FT spells, minutes-weighted MSE)
pooled kappa-bar: 7.311767 | with kappa_i: 7.309626 | gain +0.002140 (+0.029%)

## C3 — shrinkage vs exposure (dev_per48 by pooled FT possessions)
                  n    sd  max_abs
ft_poss                           
[0.0, 25.0)     257  0.44     1.78
[25.0, 50.0)    120  0.70     2.00
[50.0, 100.0)   142  1.08     2.99
[100.0, 250.0)  186  1.56     4.38
[250.0, 500.0)   75  1.97     5.11
[500.0, inf)     18  2.70     6.60

## face validity — reportable players (>= 250 FT poss, n = 93)
most negative kappa_i (per 48):
          name  ft_poss  kappa_per48
  B. Coulibaly    355.6        -0.99
   P. Banchero    323.5        -0.95
J. Jackson Jr.    851.5         0.14
     D. Powell    328.5         0.40
    D. Gafford    465.7         0.49
least negative / most positive:
      name  ft_poss  kappa_per48
 P. Siakam    675.0         7.16
  M. Smart    252.2         7.17
  T. Maxey    317.1         7.51
D. Sabonis    809.7         7.51
  J. Suggs    601.8        10.72