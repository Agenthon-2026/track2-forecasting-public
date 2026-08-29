# UST 10Y After Purchase-Pace Guidance Shifts (64 BD)

**Family** T2-F2 · **as-of 2013-05-24** · targets `UST_10Y`
at horizons [64] BD · unit `percent_per_annum` · split public-dev

Inputs mounted read-only: `/input/panels/rates_daily.parquet` (rows only through
the as-of date) and `/input/text/` (6 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** The regime signal is textual: congressional testimony 2013-05-22 ('in the next few meetings…step down the pace of purchases') and the 2013-05-01 minutes (released 2013-05-22). The panel runs through the as-of level; whether the move extends, stalls, or reverses over the horizon is the forecasting question.
