# Momentum at Peak AI Concentration (127 BD)

**Family** T2-F1 · **as-of 2024-05-31** · targets `MOM`
at horizons [127] BD · unit `cumulative_log_return` · split validation

Inputs mounted read-only: `/input/panels/factors_daily.parquet` (rows only through
the as-of date) and `/input/text/` (6 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json`. `value` = cumulative log return over the h business days after the as-of date (sum of ln(1+r_t)).


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** Momentum is unusually concentrated in one theme; central-bank texts increasingly reference AI investment. DM16 crash risk grows with crowding — the six-month cumulative distribution needs a left tail even though the trailing panel shows a smooth uptrend.
