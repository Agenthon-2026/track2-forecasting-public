# UST 10Y After a Hawkish Dot-Plot Revision (63 BD)

**Family** T2-F2 · **as-of 2023-09-20** · targets `UST_10Y`
at horizons [63] BD · unit `percent_per_annum` · split public-dev

Inputs mounted read-only: `/input/panels/rates_daily.parquet` (rows only through
the as-of date) and `/input/text/` (4 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** The projections revision restates policy restraint as a level-for-longer stance; supply commentary compounds it. The long end must decide whether to trade that signal or fade it over the horizon.
