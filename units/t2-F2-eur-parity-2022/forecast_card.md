# EUR/USD Under Energy Shock and Policy Divergence (64 BD)

**Family** T2-F2 · **as-of 2022-06-30** · targets `EUR`
at horizons [64] BD · unit `usd_per_eur` · split public-dev

Inputs mounted read-only: `/input/panels/g10_fx_daily.parquet` (rows only through
the as-of date) and `/input/text/` (6 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** Nord Stream flows cut in June; ECB speeches fight fragmentation while the Fed hikes in 75bp steps. The terms-of-trade shock and the policy divergence both live in the corpus. Whether that pressure is directional or offsetting over the horizon, and how persistent it proves, are the test.
