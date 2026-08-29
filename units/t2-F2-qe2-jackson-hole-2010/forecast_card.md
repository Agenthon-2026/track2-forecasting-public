# UST 10Y After an Easing-Options Speech (63 BD)

**Family** T2-F2 · **as-of 2010-08-31** · targets `UST_10Y`
at horizons [63] BD · unit `percent_per_annum` · split validation

Inputs mounted read-only: `/input/panels/rates_daily.parquet` (rows only through
the as-of date) and `/input/text/` (3 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** A 2010-08-27 speech (in corpus) lays out policy options for further easing; the Aug-10 statement already restarted reinvestment. Prior asset-purchase episodes show anticipation dynamics can be non-monotonic, so the window demands honest two-sided width, not a one-way drift.
