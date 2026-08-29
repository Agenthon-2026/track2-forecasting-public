# UST 2Y After a Mixed-Signal Statement and Projections (129 BD)

**Family** T2-F1 · **as-of 2015-03-18** · targets `UST_2Y`
at horizons [129] BD · unit `percent_per_annum` · split validation

Inputs mounted read-only: `/input/panels/rates_daily.parquet` (rows only through
the as-of date) and `/input/text/` (3 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** The as-of meeting pairs a hawkish edit (a time-commitment word removed from the statement) with a dovish one (projected policy paths marked down) — one meeting, two opposing signals in the same text. The 2Y must price policy timing from this tension.
