# MKT Into the New Year After Liftoff (21 BD)

**Family** T2-F4 · **as-of 2015-12-31** · targets `MKT`
at horizons [21] BD · unit `cumulative_log_return` · split validation

Inputs mounted read-only: `/input/panels/factors_daily.parquet` (rows only through
the as-of date) and `/input/text/` (6 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended; >= 1000 for tail accuracy),
plus `forecast_meta.json`. `value` = cumulative log return over the h business days after the as-of date (sum of ln(1+r_t)).


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** First hike in nine years delivered two weeks before the as-of, with China-stress commentary still circulating from the summer. The tightening cycle begins with EM fragility unresolved — the left tail must price the interaction of the two texts, not each alone.
