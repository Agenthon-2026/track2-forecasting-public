# UST 10Y as a Balance-Sheet Runoff Schedule Is Announced (127 BD)

**Family** T2-F1 · **as-of 2017-06-14** · targets `UST_10Y`
at horizons [127] BD · unit `percent_per_annum` · split validation

Inputs mounted read-only: `/input/panels/rates_daily.parquet` (rows only through
the as-of date) and `/input/text/` (3 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** As-of meeting ships an addendum describing balance-sheet normalization caps before runoff begins. Term-premium drift from an announced supply path versus still-low realized inflation — the text supplies the schedule, not the size.
