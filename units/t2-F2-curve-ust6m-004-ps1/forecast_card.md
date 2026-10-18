# UST_6M around a scheduled decision or release (1/4 BD)

**Family** T2-F2 · **as-of 2022-12-12** · targets `UST_6M`
at horizons [1, 4] BD · unit `percent_per_annum` · split public-dev

Inputs mounted read-only: `/input/panels/rates_daily.parquet` (rows only through
the as-of date) and `/input/text/` (6 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json` and `forecast_rationale.md`. `value` = level in the stated unit on the target date.

Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against realized outcomes.

**Text corpus role.** 6 official documents, all published before the as-of: 1 Beige Book, 1 FOMC statement, 2 sets of FOMC minutes and 2 statistical releases, from Federal Reserve Board and U.S. Bureau of Labor Statistics. They cover U.S. monetary policy and U.S. economic data as known before the week starts. The window holds a scheduled policy decision or data release; the corpus covers the run-up to it, not its result.
