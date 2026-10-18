# UST_3M, UST_6M, UST_1Y, UST_2Y jointly over one week (3 BD)

**Family** T2-F3 · **as-of 2010-04-26** · targets `UST_3M, UST_6M, UST_1Y, UST_2Y`
at horizons [3] BD · unit `percent_per_annum` · split public-dev

Inputs mounted read-only: `/input/panels/rates_daily.parquet` (rows only through
the as-of date) and `/input/text/` (6 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json` and `forecast_rationale.md`. `value` = level in the stated unit on the target date.
Every draw index must contain rows for ALL target assets (joint draw).

Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against realized outcomes.

**Text corpus role.** 6 official documents, all published before the as-of: 1 Beige Book, 1 FOMC statement, 1 Treasury quarterly refunding statement, 1 set of FOMC minutes and 2 statistical releases, from U.S. Department of the Treasury, Federal Reserve Board and U.S. Bureau of Labor Statistics. They cover U.S. monetary policy, U.S. economic data and Treasury financing as known before the week starts. The targets are forecast as one joint distribution.
