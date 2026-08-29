# UST 2Y at the Start of a Guided Tightening Cycle (126/189 BD)

**Family** T2-F1 · **as-of 2004-06-30** · targets `UST_2Y`
at horizons [126, 189] BD · unit `percent_per_annum` · split validation

Inputs mounted read-only: `/input/panels/rates_daily.parquet` (rows only through
the as-of date) and `/input/text/` (4 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** Statements through the first hike (as-of day): the newest guidance language conditions how quickly accommodation is expected to be removed, pinning an expected policy drift. The CRPS test is width around that text-pinned path, with symmetric weight on faster and slower outcomes.
