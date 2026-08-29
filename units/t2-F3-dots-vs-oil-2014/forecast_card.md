# Joint Curve 2015: Dots Up, Oil Down (2Y/10Y/30Y, 63/126 BD)

**Family** T2-F3 · **as-of 2014-12-17** · targets `UST_2Y, UST_10Y, UST_30Y`
at horizons [63, 126] BD · unit `percent_per_annum` · split validation

Inputs mounted read-only: `/input/panels/rates_daily.parquet` (rows only through
the as-of date) and `/input/text/` (3 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.
Every draw index must contain rows for ALL target assets (joint draw).

Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** As-of the 'patient' statement, with dots pointing to mid-2015 liftoff while the same statement flags declining energy prices. The corpus carries two OPPOSING forces: liftoff pricing pushes the front end up; oil disinflation pressures the long end down. Draws should allow opposite-sign tenor moves — parallel-shift and independent-tenor models both fail that test.
