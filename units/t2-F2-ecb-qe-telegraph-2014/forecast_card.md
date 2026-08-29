# EUR/USD Under an Escalating ECB Speech Ladder (63 BD)

**Family** T2-F2 · **as-of 2014-11-28** · targets `EUR`
at horizons [63] BD · unit `usd_per_eur` · split public-dev

Inputs mounted read-only: `/input/panels/g10_fx_daily.parquet` (rows only through
the as-of date) and `/input/text/` (14 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** All ECB presidential speeches Aug-Nov 2014, ending with late-November addresses whose commitment language escalates sharply, plus the Oct-2014 FOMC statement concluding an asset-purchase program — policy-divergence text on both legs.
