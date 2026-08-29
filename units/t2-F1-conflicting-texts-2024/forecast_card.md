# UST 10Y After a Same-Day Data/Projection Conflict (126/189 BD)

**Family** T2-F1 · **as-of 2024-06-12** · targets `UST_10Y`
at horizons [126, 189] BD · unit `percent_per_annum` · split validation

Inputs mounted read-only: `/input/panels/rates_daily.parquet` (rows only through
the as-of date) and `/input/text/` (3 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** As-of a meeting day carrying two same-day signals that point opposite ways: a soft inflation morning the statement acknowledges alongside a projection update that reads more restrictive on the pace of easing. The six-month 10Y distribution must weigh both legs, with symmetric width on higher and lower outcomes.
