# AUD Under a New Governor's Neutral Bias (126/189 BD)

**Family** T2-F1 · **as-of 2016-11-01** · targets `AUD`
at horizons [126, 189] BD · unit `usd_per_aud` · split validation

Inputs mounted read-only: `/input/panels/g10_fx_daily.parquet` (rows only through
the as-of date) and `/input/text/` (4 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** Lowe takes over with rates at 1.5% and speeches signalling comfort with the setting; commodity prices are stabilising. A long on-hold stretch where the text argues for range, not trend — width discipline is the score.
