# UST 10Y Under Supply and Dot Pressure (21 BD)

**Family** T2-F4 · **as-of 2023-09-29** · targets `UST_10Y`
at horizons [21] BD · unit `percent_per_annum` · split validation

Inputs mounted read-only: `/input/panels/rates_daily.parquet` (rows only through
the as-of date) and `/input/text/` (3 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended; >= 1000 for tail accuracy),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** Quarter-end after the dot shock: supply commentary, shutdown-risk texts and higher-for-longer language stack on the long end, with recent momentum adverse. Weigh continuation of the text-driven repricing against mean-reversion after a large move — both branches are live.
