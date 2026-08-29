# Systemic-Stress Factor Joint: MKT + QMJ (21 BD)

**Family** T2-F4 · **as-of 2008-09-12** · targets `MKT, QMJ`
at horizons [21] BD · unit `cumulative_log_return` · split validation

Inputs mounted read-only: `/input/panels/factors_daily.parquet` (rows only through
the as-of date) and `/input/text/` (5 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended; >= 1000 for tail accuracy),
plus `forecast_meta.json`. `value` = cumulative log return over the h business days after the as-of date (sum of ln(1+r_t)).
Every draw index must contain rows for ALL target assets (joint draw).

Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** The factor expression of the pre-shock September-2008 corpus: whether a systemic branch materializes, and how the market and quality-minus-junk legs co-move in it, is the forecasting question. Draw the two legs as one coherent joint scenario (a conditional correlation that can tighten in the tail), not independent per-asset noise.
