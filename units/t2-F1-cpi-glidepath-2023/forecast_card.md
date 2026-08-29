# CPI Index Level Six Months Out: the Base-Effect Glidepath (140/160 BD)

**Family** T2-F1 · **as-of 2023-07-12** · targets `CPI_ALL`
at horizons [140, 160] BD · unit `cpi_index_1982_84_100 (current vintage; see notes)` · split public-dev

Inputs mounted read-only: `/input/panels/macro_monthly.parquet` (rows only through
the as-of date) and `/input/text/` (3 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** As-of the June-2023 CPI release day (3.0% YoY). Base effects mechanically push YoY back up over the summer — the arithmetic is knowable from published index levels; energy and the last-mile services trend are the swing factors. Forecast the January and February 2024 index levels — a six-month inflation path, not a nowcast.
