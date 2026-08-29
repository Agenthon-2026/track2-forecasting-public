# CAD as the Bank of Canada Turns (126/189 BD)

**Family** T2-F1 · **as-of 2017-07-12** · targets `CAD`
at horizons [126, 189] BD · unit `cad_per_usd` · split validation

Inputs mounted read-only: `/input/panels/g10_fx_daily.parquet` (rows only through
the as-of date) and `/input/text/` (4 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** Deputy-governor remarks in June 2017 telegraph that the 2015 insurance cuts 'have done their job'; the July hike lands at the as-of. With the turn delivered and telegraphed, the six-month question is follow-through pace versus oil and NAFTA noise.
