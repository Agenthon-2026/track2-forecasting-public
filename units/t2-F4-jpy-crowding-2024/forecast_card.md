# USD/JPY Tail Risk at Peak Carry Crowding (21 BD)

**Family** T2-F4 · **as-of 2024-07-31** · targets `JPY`
at horizons [21] BD · unit `jpy_per_usd` · split public-dev

Inputs mounted read-only: `/input/panels/g10_fx_daily.parquet` (rows only through
the as-of date) and `/input/text/` (4 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended; >= 1000 for tail accuracy),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** BoJ 2024-07-31 hike + taper decision, March NIRP-exit context, the same-day FOMC statement, and the CFTC COT table showing speculative yen shorts near record extremes. BNP08 carry-crash conditions: a shrinking rate differential plus crowded positioning is the regime; whether the carry trade unwinds over the horizon is the forecasting question, so the tail deserves far more mass than trailing vol suggests.
