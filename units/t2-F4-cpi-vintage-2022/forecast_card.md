# Monthly CPI Print: Tail Risk from Real-Time Price Texts (as-published vintage)

**Family** T2-F4 · **as-of 2022-05-31** · targets `CPI_ALL`
at horizons [21] BD · unit `cpi_index_1982_84_100_vintage_2022_07_13` · split public-dev

Inputs mounted read-only: `/input/panels/macro_monthly.parquet` (rows only through
the as-of date) and `/input/text/` (5 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended; >= 1000 for tail accuracy),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** Forecast the next CPI index level AS FIRST PUBLISHED — targets use the as-published (first-release) values, not later revisions (see data/vintage_example/). Panel truncated with a 45-day publication lag: the intervening print was not yet public at the as-of date. Prior CPI release texts (in corpus) document the recent trend and breadth commentary; real-time energy-price discussion is the incremental signal the panel cannot show yet, and the sign and size of the surprise remain open.
