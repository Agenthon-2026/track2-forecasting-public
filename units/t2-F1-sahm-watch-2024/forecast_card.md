# Unemployment Six Months After a Recession-Rule Trigger (145/165 BD)

**Family** T2-F1 · **as-of 2024-08-02** · targets `UNRATE`
at horizons [145, 165] BD · unit `percent (U-3, current vintage)` · split public-dev

Inputs mounted read-only: `/input/panels/macro_monthly.parquet` (rows only through
the as-of date) and `/input/text/` (6 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** As-of the July-2024 jobs report day: the unemployment rise trips a standard statistical recession rule — but Fed texts argue the rise reflects labor-supply normalization, not demand collapse. Two mechanisms with opposite six-month implications: recessions compound, supply normalizations plateau. Forecast the January and February 2025 rates.
