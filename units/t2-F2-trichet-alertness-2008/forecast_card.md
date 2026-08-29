# EUR/USD After a Hawkish Signal at a Possible Cycle Peak (64 BD)

**Family** T2-F2 · **as-of 2008-06-30** · targets `EUR`
at horizons [64] BD · unit `usd_per_eur` · split validation

Inputs mounted read-only: `/input/panels/g10_fx_daily.parquet` (rows only through
the as-of date) and `/input/text/` (11 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** June 2008 policy communication signals imminent tightening on headline inflation while growth and credit commentary deteriorates in the same corpus. Two branches compete ex-ante: the rate-differential reading (euro-supportive) and the policy-error/cycle-turn reading (euro-negative). Weigh both; neither text should be taken at face value.
