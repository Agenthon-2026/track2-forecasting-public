# UST 2Y After a Cut Paired with Shallower Rate-Path Guidance (126/189 BD)

**Family** T2-F1 · **as-of 2024-12-18** · targets `UST_2Y`
at horizons [126, 189] BD · unit `percent_per_annum` · split public-dev

Inputs mounted read-only: `/input/panels/rates_daily.parquet` (rows only through
the as-of date) and `/input/text/` (3 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** As-of the December 2024 meeting: a 25bp cut delivered together with a dot plot cut from four 2025 cuts to two and new 'extent and timing' caution. November minutes (released 2024-11-26) already flag upside inflation risk and tariff-platform uncertainty. The 2Y must weigh a shallower cut path against tariff-cycle growth risk.
