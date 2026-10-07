# UST 2Y After a Cut Paired with Shallower Rate-Path Guidance (126/189 BD)

**Family** T2-F1 · **as-of 2024-12-18** · targets `UST_2Y`
at horizons [126, 189] BD · unit `percent_per_annum` · split public-dev

Inputs mounted read-only: `/input/panels/rates_daily.parquet` (rows only through
the as-of date) and `/input/text/` (8 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** As-of the December 2024 meeting: a 25bp cut, a revised dot plot for 2025 and new 'extent and timing' language in the statement. The November minutes (released 2024-11-26) discuss inflation risks, and the Beige Book released 2024-12-04 records tariff uncertainty. The documents bear on the 2025 policy path and on tariff-cycle growth risk.
