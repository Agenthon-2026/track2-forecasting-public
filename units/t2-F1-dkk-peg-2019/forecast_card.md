# DKK Under the ERM-II Peg: an Honest-Width Test (129 BD)

**Family** T2-F1 · **as-of 2019-03-01** · targets `DKK`
at horizons [129] BD · unit `dkk_per_usd` · split validation

Inputs mounted read-only: `/input/panels/g10_fx_daily.parquet` (rows only through
the as-of date) and `/input/text/` (5 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** DKK is pegged to EUR (ERM-II +-2.25%, in practice far tighter), so USD/DKK is EUR/USD in disguise; ECB texts drive it. The honest distribution is EXTREMELY narrow around the EUR path — lazy wide tails are punished by CRPS over-dispersion (GR07).
