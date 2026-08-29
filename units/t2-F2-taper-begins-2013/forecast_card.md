# UST 10Y as Purchases Slow and Guidance Strengthens (126 BD)

**Family** T2-F2 · **as-of 2013-12-18** · targets `UST_10Y`
at horizons [126] BD · unit `percent_per_annum` · split validation

Inputs mounted read-only: `/input/panels/rates_daily.parquet` (rows only through
the as-of date) and `/input/text/` (3 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** A long-anticipated reduction in the purchase pace arrives at the as-of meeting, paired with strengthened forward guidance. The corpus therefore contains BOTH a supply-negative and a guidance-positive signal, and positioning commentary at the as-of is one-sided. Weigh the two texts and the positioning evidence without presuming which force dominates over the horizon.
