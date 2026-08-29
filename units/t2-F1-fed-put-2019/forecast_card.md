# Cumulative Market Factor Return After a Dovish Policy Pivot (128 BD)

**Family** T2-F1 · **as-of 2019-06-04** · targets `MKT`
at horizons [128] BD · unit `cumulative_log_return` · split validation

Inputs mounted read-only: `/input/panels/factors_daily.parquet` (rows only through
the as-of date) and `/input/text/` (4 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json`. `value` = cumulative log return over the h business days after the as-of date (sum of ln(1+r_t)).


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** As-of a dovish opening-remarks pivot signalling readiness to support the expansion amid trade-war stress; MKT rose on the speech day. Does the supportive-policy regime hold over the six months that follow?
