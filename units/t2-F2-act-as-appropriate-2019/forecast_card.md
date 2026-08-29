# UST 2Y as Insurance Cuts Are Telegraphed (64 BD)

**Family** T2-F2 · **as-of 2019-06-19** · targets `UST_2Y`
at horizons [64] BD · unit `percent_per_annum` · split validation

Inputs mounted read-only: `/input/panels/rates_daily.parquet` (rows only through
the as-of date) and `/input/text/` (4 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** June 2019 statement drops its patience language; eight participants dot a 2019 cut; the chair's early-June remarks signal a readiness to respond as needed. The easing regime is being announced in stages — the size and count of cuts is the remaining uncertainty.
