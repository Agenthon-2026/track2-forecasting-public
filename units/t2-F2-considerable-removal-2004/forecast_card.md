# UST 2Y as the Exit Language Begins (63 BD)

**Family** T2-F2 · **as-of 2004-01-30** · targets `UST_2Y`
at horizons [63] BD · unit `percent_per_annum` · split validation

Inputs mounted read-only: `/input/panels/rates_daily.parquet` (rows only through
the as-of date) and `/input/text/` (3 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** The January 2004 statement changes only its forward-guidance wording — the duration phrase is replaced by a patience phrase, a pure language change with no action — and the two-year repriced sharply on release. The regime question: how fast does the patience language become hikes?
