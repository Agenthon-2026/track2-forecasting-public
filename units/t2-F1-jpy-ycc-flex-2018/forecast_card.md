# USD/JPY After the 2018 YCC Flexibility Tweak (126/189 BD)

**Family** T2-F1 · **as-of 2018-07-31** · targets `JPY`
at horizons [126, 189] BD · unit `jpy_per_usd` · split validation

Inputs mounted read-only: `/input/panels/g10_fx_daily.parquet` (rows only through
the as-of date) and `/input/text/` (5 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** BoJ widens the tolerated 10Y JGB band while insisting easing persists — a tweak dressed as continuity. Distinguishing a technical adjustment from the start of normalization is precisely the text-reading task; the rate differential still dominates the level.
