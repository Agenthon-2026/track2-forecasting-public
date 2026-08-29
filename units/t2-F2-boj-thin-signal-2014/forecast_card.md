# USD/JPY Into a Thin-Signal BoJ Window (63 BD)

**Family** T2-F2 · **as-of 2014-10-24** · targets `JPY`
at horizons [63] BD · unit `jpy_per_usd` · split public-dev

Inputs mounted read-only: `/input/panels/g10_fx_daily.parquet` (rows only through
the as-of date) and `/input/text/` (4 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** Autumn governor speeches defend the inflation goal as oil drags inflation down and a major easing program's anniversary approaches — grounds for suspicion, not confirmation, of a policy shift in either direction. The card tests whether stated uncertainty is calibrated to the strength of the pre-as-of evidence.
