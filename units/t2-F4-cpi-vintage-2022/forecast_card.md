# Monthly CPI Print: Tail Risk from Real-Time Price Texts (as-published vintage)

**Family** T2-F4 · **as-of 2022-05-31** · targets `CPI_ALL`
at horizons [21] BD · unit `cpi_index_1982_84_100_vintage_2022_07_13` · split public-dev

Inputs mounted read-only: `/input/panels/macro_monthly.parquet` (rows only through
the as-of date) and `/input/text/` (10 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended; >= 1000 for tail accuracy),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.

Panel values are the vintage as published on the as-of date (31 May 2022), not later revisions; PCE indexes are on the base then in force (2012=100, not today's 2017=100).

Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** Forecast the June 2022 CPI index level AS FIRST PUBLISHED (released in July 2022), one print beyond the May 2022 print that is next at the as-of date — targets use the as-published (first-release) values, not later revisions (see docs/CATEGORIES.md and docs/MONTHLY-HORIZONS.md). Panel truncated with a 45-day publication lag: its last observation is April 2022, and the intervening May 2022 print was not yet public at the as-of date. Prior CPI release texts (in corpus) document the recent trend and breadth commentary; real-time energy-price discussion is the incremental signal the panel cannot show yet, and the sign and size of the surprise remain open.
