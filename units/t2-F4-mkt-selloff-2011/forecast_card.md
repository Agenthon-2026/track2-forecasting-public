# MKT Through the Debt-Ceiling Endgame (21 BD)

**Family** T2-F4 · **as-of 2011-07-22** · targets `MKT`
at horizons [21] BD · unit `cumulative_log_return` · split validation

Inputs mounted read-only: `/input/panels/factors_daily.parquet` (rows only through
the as-of date) and `/input/text/` (5 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended; >= 1000 for tail accuracy),
plus `forecast_meta.json`. `value` = cumulative log return over the h business days after the as-of date (sum of ln(1+r_t)).


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** Companion to the rates card at the same as-of: brinkmanship texts with the X-date inside the window, a rating agency on record, and European stress in the background. Equity draws need a fat left tail for the confidence-shock branch and a relief branch for a deal — the panel's calm summer tape prices neither.
