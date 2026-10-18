# UST_3M: short-horizon continuation (2/3 BD)

**Family** T2-F1 · **as-of 2021-06-07** · targets `UST_3M`
at horizons [2, 3] BD · unit `percent_per_annum` · split public-dev

Inputs mounted read-only: `/input/panels/rates_daily.parquet` (rows only through
the as-of date) and `/input/text/` (6 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json` and `forecast_rationale.md`. `value` = level in the stated unit on the target date.

Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against realized outcomes.

**Text corpus role.** 6 official documents, all published before the as-of: 1 Beige Book, 1 FOMC statement, 1 Treasury quarterly refunding statement, 1 set of FOMC minutes and 2 statistical releases, from Federal Reserve Board, U.S. Department of the Treasury and U.S. Bureau of Labor Statistics. They cover U.S. monetary policy, U.S. economic data and Treasury financing as known before the week starts. They are background for a one-week continuation of the panel.
