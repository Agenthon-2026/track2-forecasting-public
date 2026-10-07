# USD/JPY Carry Under Subprime Funding Stress (21 BD)

**Family** T2-F4 · **as-of 2007-07-20** · targets `JPY`
at horizons [21] BD · unit `jpy_per_usd` · split validation

Inputs mounted read-only: `/input/panels/g10_fx_daily.parquet` (rows only through
the as-of date) and `/input/text/` (12 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended; >= 1000 for tail accuracy),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** The COT table in the corpus shows large net speculative yen shorts through 2007, and texts on deteriorating subprime mortgage credit accumulate through July (the Fed chair's July testimony, the June minutes released 19 July). The documents bear on crowded funding-currency positioning together with building credit stress; how that combination plays out over the horizon is the forecasting question.
