# One Print, Two Factors: MKT + HML Through a CPI Release (21/63 BD)

**Family** T2-F3 · **as-of 2022-09-09** · targets `MKT, HML`
at horizons [21, 63] BD · unit `cumulative_log_return` · split validation

Inputs mounted read-only: `/input/panels/factors_daily.parquet`, `/input/panels/rates_daily.parquet` (rows only through
the as-of date) and `/input/text/` (4 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json`. `value` = cumulative log return over the h business days after the as-of date (sum of ln(1+r_t)).
Every draw index must contain rows for ALL target assets (joint draw).

Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** A CPI release date falls inside the horizon (known ex-ante) with Jackson Hole still ringing. The surprise branches must move MKT and HML together within each draw (rate-sensitive growth carries the factor exposure), so the two legs form a coherent joint scenario rather than independent per-factor noise. Signed co-movement through the print is the joint test.
