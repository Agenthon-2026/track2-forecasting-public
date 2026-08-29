# USD/JPY as Political and Institutional Texts Conflict (63 BD)

**Family** T2-F2 · **as-of 2012-11-30** · targets `JPY`
at horizons [63] BD · unit `jpy_per_usd` · split public-dev

Inputs mounted read-only: `/input/panels/g10_fx_daily.parquet` (rows only through
the as-of date) and `/input/text/` (4 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** An election has been called and the opposition platform demands a far more accommodative monetary regime with an explicit inflation objective; the sitting governor's speeches (in corpus) push back on central-bank-independence grounds. The regime question is whether political text overrides institutional text — and how much of a decade-old currency regime reprices if it does.
