# UST 2Y After a Signalled Pause in an Easing Sequence (126/189 BD)

**Family** T2-F1 · **as-of 2019-10-30** · targets `UST_2Y`
at horizons [126, 189] BD · unit `percent_per_annum` · split public-dev

Inputs mounted read-only: `/input/panels/rates_daily.parquet` (rows only through
the as-of date) and `/input/text/` (3 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** Third consecutive cut with language shifting to 'the current stance…will likely remain appropriate' — a signalled pause. The honest six-month distribution keeps meaningful width in BOTH directions for states the text cannot anticipate.
