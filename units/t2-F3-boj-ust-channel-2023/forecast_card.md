# One Policy Decision, Two Markets: UST 10Y + JPY (21/63 BD)

**Family** T2-F3 · **as-of 2023-07-21** · targets `UST_10Y, JPY`
at horizons [21, 63] BD · unit `percent_per_annum (UST_10Y); JPY-per-USD` · split public-dev

Inputs mounted read-only: `/input/panels/rates_daily.parquet`, `/input/panels/g10_fx_daily.parquet` (rows only through
the as-of date) and `/input/text/` (6 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.
Every draw index must contain rows for ALL target assets (joint draw).

Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** A foreign central-bank policy meeting sits inside the window, with policy-framework speculation present in the corpus. A repatriation channel ties the two targets: in the policy-shift branch, UST yields and the FX leg move TOGETHER; in the no-change branch the historical linkage prevails. Draws must correlate the two legs through the policy branch, not through their historical beta; neither branch is privileged a priori.
