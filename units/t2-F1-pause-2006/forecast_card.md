# UST 2Y and 10Y Through the 2006 Pause (126/189 BD)

**Family** T2-F1 · **as-of 2006-08-08** · targets `UST_2Y, UST_10Y`
at horizons [126, 189] BD · unit `percent_per_annum` · split validation

Inputs mounted read-only: `/input/panels/rates_daily.parquet` (rows only through
the as-of date) and `/input/text/` (3 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.
Every draw index must contain rows for ALL target assets (joint draw).

Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** After 17 consecutive hikes the August 2006 statement holds, keeping 'some inflation risks remain'. A data-dependent plateau: the text rules out imminent cuts while leaving the hiking option open. Width and the 2s10s relationship over six months are the test.
