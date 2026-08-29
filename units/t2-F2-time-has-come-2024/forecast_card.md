# UST 2Y After an Explicit Easing-Pivot Signal (63 BD)

**Family** T2-F2 · **as-of 2024-08-23** · targets `UST_2Y`
at horizons [63] BD · unit `percent_per_annum` · split public-dev

Inputs mounted read-only: `/input/panels/rates_daily.parquet` (rows only through
the as-of date) and `/input/text/` (4 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** A late-August 2024 policy address (as-of day) signals that a rate-cut cycle is about to begin. Cutting is certain; the SIZE of the first move and the path into November are not. July minutes (released 2024-08-21) lean dovish.
