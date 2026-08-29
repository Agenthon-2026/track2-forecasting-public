# USD/JPY the Week After a Policy-Rate Cut Below Zero (63 BD)

**Family** T2-F2 · **as-of 2016-02-05** · targets `JPY`
at horizons [63] BD · unit `jpy_per_usd` · split public-dev

Inputs mounted read-only: `/input/panels/g10_fx_daily.parquet` (rows only through
the as-of date) and `/input/text/` (6 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** A week after a surprise negative-rate adoption, the governor's defence of the framework is in corpus alongside the European negative-rate experience. Textbook transmission says easier policy weakens the currency; the European texts document cases where bank-profitability and risk-appetite channels cut the other way. Decide which mechanism governs — and how fast.
