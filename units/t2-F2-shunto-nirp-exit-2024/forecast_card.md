# USD/JPY Through a Telegraphed BoJ Policy-Rate Exit (65 BD)

**Family** T2-F2 · **as-of 2024-03-15** · targets `JPY`
at horizons [65] BD · unit `jpy_per_usd` · split public-dev

Inputs mounted read-only: `/input/panels/g10_fx_daily.parquet` (rows only through
the as-of date) and `/input/text/` (5 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** BoJ speeches through the spring condition exit on confirmation of the wage-price 'virtuous cycle', and the first wage-round tally lands the same week as the as-of. The corpus shows the event is close to fully telegraphed and largely priced; when an event is priced, the forecastable component shifts to the rate differential (carry) rather than the event itself. The direction of the currency over the horizon need not follow the direction of the policy move.
