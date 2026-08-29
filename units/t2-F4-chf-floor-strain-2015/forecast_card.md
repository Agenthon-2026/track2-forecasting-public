# CHF Under a Defended-Floor Regime (21 BD)

**Family** T2-F4 · **as-of 2014-12-19** · targets `CHF`
at horizons [21] BD · unit `chf_per_usd` · split public-dev

Inputs mounted read-only: `/input/panels/g10_fx_daily.parquet` (rows only through
the as-of date) and `/input/text/` (9 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended; >= 1000 for tail accuracy),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** A reassuring-text setting: one central bank restates its commitment to an announced floor (and introduces negative rates), while a second bank's corpus signals policy that changes the cost of holding that regime. The tail warrant is the tension between the two corpora rather than either alone; the direction and timing of any regime change over the horizon are left open.
