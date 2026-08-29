# UST 2Y After an Intermeeting Policy Statement (63 BD)

**Family** T2-F2 · **as-of 2007-08-17** · targets `UST_2Y`
at horizons [63] BD · unit `percent_per_annum` · split validation

Inputs mounted read-only: `/input/panels/rates_daily.parquet` (rows only through
the as-of date) and `/input/text/` (6 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** Three statements in ten days shift in their characterization of risks and include an administered-rate action; the sequence itself is information. Whether it marks a durable change in the policy path, and how far the front end moves over the horizon, is the question.
