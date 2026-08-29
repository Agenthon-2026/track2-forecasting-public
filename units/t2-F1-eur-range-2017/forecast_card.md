# EUR/USD After Verbal Intervention on FX Strength (126/189 BD)

**Family** T2-F1 · **as-of 2017-09-07** · targets `EUR`
at horizons [126, 189] BD · unit `usd_per_eur` · split validation

Inputs mounted read-only: `/input/panels/g10_fx_daily.parquet` (rows only through
the as-of date) and `/input/text/` (3 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** A central-bank press conference flags the exchange rate as a source of uncertainty requiring monitoring after a strong currency run — classic soft verbal intervention. Historically such language can dampen trend extension; the test is drift versus range.
