# MKT Tail From Offshore Stress (21 BD)

**Family** T2-F4 · **as-of 2015-07-31** · targets `MKT`
at horizons [21] BD · unit `cumulative_log_return` · split validation

Inputs mounted read-only: `/input/panels/factors_daily.parquet` (rows only through
the as-of date) and `/input/text/` (8 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended; >= 1000 for tail accuracy),
plus `forecast_meta.json`. `value` = cumulative log return over the h business days after the as-of date (sum of ln(1+r_t)).


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** US equities sit near highs on a calm panel while the corpus documents offshore equity stress and global risk commentary. If the offshore stress forces a currency-regime response, the transmission to US equities can be fast and fat-tailed; the panel itself gives no warning, and the direction and size of any transmission over the horizon are left open.
